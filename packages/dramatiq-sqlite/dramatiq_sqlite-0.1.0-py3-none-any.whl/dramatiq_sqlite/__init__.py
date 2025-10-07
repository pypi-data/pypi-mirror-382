import json
import logging
import os
import sqlite3
import time
from random import randint
from threading import Lock

from dramatiq import Message, MessageProxy, get_encoder
from dramatiq.broker import Broker, Consumer, MessageProxy
from dramatiq.common import compute_backoff, current_millis, dq_name
from dramatiq.message import Message
from dramatiq.results import ResultBackend, Results


logger = logging.getLogger(__name__)


class SQLiteResultBackend(ResultBackend):
    def __init__(self, *, url, **kwargs):
        super().__init__(**kwargs)
        self.db = Database.create(url)

    def _get(self, message_key):
        with self.db as cursor:
            cursor.execute("SELECT result FROM dramatiq_results WHERE message_id = ?", (message_key,))
            row = cursor.fetchone()
            if row:
                return row[0]
        return None
    
    def _store(self, message_key, result, ttl):
        with self.db as cursor:
            expiration = int(time.time()) + int(ttl / 1000)
            cursor.execute(
                "INSERT OR REPLACE INTO dramatiq_results VALUES (?, ?, ?)",
                (message_key, json.dumps(result), expiration)
            )
    
    def cleanup(self):
        with self.db as cursor:
            cursor.execute("DELETE FROM dramatiq_results WHERE expiration < ?", (int(time.time()),))


class SQLiteBroker(Broker):
    def __init__(
        self,
        *,
        url,
        results=False,
        **kw
    ):
        super().__init__(**kw)
        self.db_url = url
        self.db = Database.create(url)
        self.backend = None
        if results:
            self.backend = SQLiteResultBackend(url=url)
            self.add_middleware(Results(backend=self.backend))

    def consume(self, queue_name, prefetch=1, timeout=30000):
        return SQLiteConsumer(
            url=self.db_url,
            queue_name=queue_name,
            prefetch=prefetch,
            timeout=timeout
        )

    def declare_queue(self, queue_name):
        if queue_name not in self.queues:
            self.emit_before("declare_queue", queue_name)
            self.queues[queue_name] = True
            # No need to create anything for SQLite
            self.emit_after("declare_queue", queue_name)

            delayed_name = dq_name(queue_name)
            self.delay_queues.add(delayed_name)
            self.emit_after("declare_delay_queue", delayed_name)

    def enqueue(self, message, *, delay=None):
        self.emit_before("enqueue", message, delay)
        if delay:
            message = message.copy(queue_name=dq_name(message.queue_name))
            message.options["eta"] = current_millis() + delay

        queue_name = message.queue_name
        logger.debug("Upserting %s in queue %s.", message.message_id, queue_name)
        
        with self.db as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO dramatiq_messages 
                (message_id, queue_name, state, message, mtime) 
                VALUES (?, ?, 'queued', ?, ?)
                """,
                (
                    message.message_id,
                    queue_name,
                    json.dumps(tidy4json(message)),
                    int(time.time())
                )
            )
        
        self.emit_after("enqueue", message, delay)
        return message


class SQLiteConsumer(Consumer):
    def __init__(self, *, url, queue_name, prefetch, timeout, **kw):
        self.db = Database.create(url)
        self.queue_name = queue_name
        self.timeout = timeout // 1000
        self.prefetch = prefetch
        self.misses = 0
        self.in_processing = set()

    def __next__(self):
        # Check if we're at prefetch limit
        processing = len(self.in_processing)
        if processing >= self.prefetch:
            self.misses, backoff_ms = compute_backoff(
                self.misses, max_backoff=1000
            )
            logger.debug(
                f"Too many messages in processing: {processing} sleeping {backoff_ms}"
            )
            time.sleep(backoff_ms / 1000)
            return None

        # Find pending messages in queue
        with self.db as cursor:
            cursor.execute(
                """
                SELECT message FROM dramatiq_messages 
                WHERE queue_name = ? AND state = 'queued'
                LIMIT 1
                """,
                (self.queue_name,)
            )
            row = cursor.fetchone()
            
        if row:
            # Try to consume it
            message = Message.decode(row["message"].encode("utf-8"))
            if self.consume_one(message):
                return MessageProxy(message)
            else:
                logger.debug(
                    "Message %s already consumed. Skipping.",
                    message.message_id,
                )

        # Occasionally purge old messages
        if not randint(0, 100_000):
            self.auto_purge()

        # No message found, wait a bit before next try
        time.sleep(0.1)
        return None

    def consume_one(self, message):
        if message.message_id in self.in_processing:
            logger.debug("%s already consumed by self.", message.message_id)
            return False

        # Attempt to mark as consumed
        with self.db as cursor:
            cursor.execute(
                """
                UPDATE dramatiq_messages
                SET state = 'consumed', mtime = ?
                WHERE message_id = ? AND state = 'queued'
                """,
                (int(time.time()), message.message_id)
            )
            
            if cursor.rowcount:
                self.in_processing.add(message.message_id)
                logger.debug(
                    "Consumed %s@%s.", message.message_id, message.queue_name
                )
                return True
            return False

    def ack(self, message):
        with self.db as cursor:
            logger.debug(
                "Marking message %s as done.", message.message_id
            )
            cursor.execute(
                """
                UPDATE dramatiq_messages
                SET state = 'done', message = ?, mtime = ?
                WHERE message_id = ? AND queue_name = ?
                """,
                (
                    json.dumps(tidy4json(message)),
                    int(time.time()),
                    message.message_id,
                    message.queue_name
                )
            )
        self.in_processing.remove(message.message_id)

    def nack(self, message):
        with self.db as cursor:
            logger.debug(
                "Marking message %s as rejected.", message.message_id
            )
            cursor.execute(
                """
                UPDATE dramatiq_messages
                SET state = 'rejected', message = ?, mtime = ?
                WHERE message_id = ? AND queue_name = ?
                """,
                (
                    json.dumps(tidy4json(message)),
                    int(time.time()),
                    message.message_id,
                    message.queue_name
                )
            )
        self.in_processing.remove(message.message_id)

    def requeue(self, messages):
        messages = list(messages)
        if not len(messages):
            return

        with self.db as cursor:
            logger.debug("Batch update of messages for requeue.")
            cursor.execute(
                """
                UPDATE dramatiq_messages
                SET state = 'queued', mtime = ?
                WHERE message_id IN ?
                """,
                (int(time.time()), tuple(m.message_id for m in messages))
            )

    def auto_purge(self):
        logger.debug("Randomly triggering garbage collector.")
        cutoff = int(time.time()) - 30*24*60*60  # 30 days
        with self.db as cursor:
            cursor.execute(
                """
                DELETE FROM dramatiq_messages
                WHERE state IN ('done', 'rejected')
                AND mtime <= ?
                """,
                (cutoff,)
            )
            logger.info("Purged %d messages in all queues.", cursor.rowcount)


class Database:
    concurrent_workload_pragmas = {
        "journal_mode": "WAL",
        "synchronous": "NORMAL",
        "journal_size_limit": "67108864",  # 64mb
        "mmap_size": "134217728",  # 128mb
        "cache_size": "2000",
        "busy_timeout": "5000",
    }
    
    @classmethod
    def create(cls, url):
        if isinstance(url, cls):
            return url
        if isinstance(url, sqlite3.Connection):
            return cls(url)
        if url.startswith("sqlite://"):
            url = url[9:]
        if url == ":memory:":
            raise Exception("In-memory database not supported.")
        os.makedirs(os.path.dirname(os.path.abspath(url)), exist_ok=True)
        conn = sqlite3.connect(url, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        for key, value in cls.concurrent_workload_pragmas.items():
            conn.execute(f"PRAGMA {key} = {value}")
        return cls(conn)

    def __init__(self, conn):
        self.conn = conn
        self.lock = Lock()
        self.cursor = None
        self.init_schema()

    def init_schema(self):
        with self as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dramatiq_results (
                message_id TEXT PRIMARY KEY,
                result BLOB,
                expiration INTEGER
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expiration ON dramatiq_results(expiration)")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dramatiq_messages (
                message_id TEXT PRIMARY KEY,
                queue_name TEXT NOT NULL,
                state TEXT NOT NULL,
                message TEXT NOT NULL,
                mtime INTEGER NOT NULL
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_queue_state ON dramatiq_messages(queue_name, state)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_mtime ON dramatiq_messages(mtime)")

    def __enter__(self):
        self.lock.acquire()
        self.cursor = self.conn.cursor()
        return self.cursor
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.cursor.close()
            self.cursor = None
        finally:
            self.lock.release()


def tidy4json(data):
    if isinstance(data, (Message, MessageProxy)):
        # Translate python data into decoded json.
        # Encode message using Dramatiq encoder. But immediatly decode it as
        # standard json to send native json to PostgreSQL.
        # e.g. date formating problem
        return json.loads(data.encode())
    else:
        return json.loads(get_encoder().encode(data))
