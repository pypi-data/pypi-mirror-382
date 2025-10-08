from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

from ..logger import create_logger
from .base import DeliveryConfig, DeliveryType, QueueDelivery, QueueItem


class PersistentDelivery(QueueDelivery):
    """Durable queue based delivery using SQLite."""

    type = DeliveryType.PERSISTENT_QUEUE

    def __init__(
        self,
        *,
        config: DeliveryConfig | None = None,
        db_path: str | None = None,
        poll_interval: float = 0.1,
        batch_interval: float = 0.5,
        max_attempts: int = 3,
        max_retries: int = 5,
        log_bodies: bool = False,
        max_batch_size: int = 1000,
        logger: logging.Logger | None = None,
    ) -> None:
        # Create default config if none provided
        if config is None:
            from ..ini_manager import IniManager

            ini_manager = IniManager(IniManager.resolve_path(None))
            ini_dir = Path(ini_manager.ini_path).resolve().parent

            def _get(option: str, default: str | None = None) -> str | None:
                return ini_manager.get_option("tracker", option, default)

            # Read configuration from INI file, then environment variables, then defaults
            api_base = (
                _get("AICM_API_BASE")
                or os.getenv("AICM_API_BASE")
                or "https://aicostmanager.com"
            )
            api_url = _get("AICM_API_URL") or os.getenv("AICM_API_URL") or "/api/v1"
            log_file = (
                _get("AICM_LOG_FILE")
                or os.getenv("AICM_LOG_FILE")
                or str(ini_dir / "aicm.log")
            )
            log_level = _get("AICM_LOG_LEVEL") or os.getenv("AICM_LOG_LEVEL")
            timeout = float(
                _get("AICM_TIMEOUT") or os.getenv("AICM_TIMEOUT") or "10.0"
            )
            immediate_pause_seconds = float(
                _get("AICM_IMMEDIATE_PAUSE_SECONDS")
                or os.getenv("AICM_IMMEDIATE_PAUSE_SECONDS")
                or "5.0"
            )

            config = DeliveryConfig(
                ini_manager=ini_manager,
                aicm_api_key=os.getenv("AICM_API_KEY"),
                aicm_api_base=api_base,
                aicm_api_url=api_url,
                timeout=timeout,
                log_file=log_file,
                log_level=log_level,
                immediate_pause_seconds=immediate_pause_seconds,
            )

        # Create default db_path if none provided
        if db_path is None:
            # Precedence: INI setting > environment variable > default path
            # Check if db_path was provided in config's INI file
            if hasattr(config, "ini_manager"):
                ini_db_path = config.ini_manager.get_option("tracker", "AICM_DB_PATH")
                if ini_db_path:
                    db_path = ini_db_path

            # Fall back to environment variable
            if db_path is None:
                env_db_path = os.getenv("AICM_DB_PATH")
                if env_db_path:
                    db_path = env_db_path

            # If still None, use default path alongside the INI file
            if db_path is None and hasattr(config, "ini_manager"):
                ini_dir = Path(config.ini_manager.ini_path).resolve().parent
                db_path = str(ini_dir / "queue.db")

        # Initialize logger first so we can use it during database setup
        self.logger = logger or create_logger(
            self.__class__.__name__, config.log_file, config.log_level
        )

        # Initialize DB-related attributes and locking BEFORE starting worker thread
        self.db_path = db_path
        self.poll_interval = poll_interval
        self.log_bodies = log_bodies
        self._closed = False
        self._final_stats: Dict[str, Any] | None = None

        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with self.conn:
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    scheduled_at REAL NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
        # Reset any in-flight messages and surface existing failures
        with self.conn:
            now = time.time()
            self.conn.execute(
                "UPDATE queue SET status='queued', scheduled_at=?, updated_at=? WHERE status='processing'",
                (now, now),
            )
            cur = self.conn.execute("SELECT COUNT(*) FROM queue WHERE status='failed'")
            (failed_count,) = cur.fetchone()
            if failed_count:
                self.logger.warning(
                    "%d failed items present in persistent queue. "
                    "Use PersistentQueueManager('%s') to inspect or requeue. "
                    "See docs/persistent_queue_manager.md for details.",
                    failed_count,
                    self.db_path,
                )
        self._lock = threading.Lock()

        # Start background worker after we are fully initialized
        super().__init__(
            config,
            batch_interval=batch_interval,
            max_batch_size=max_batch_size,
            max_attempts=max_attempts,
            max_retries=max_retries,
            logger=self.logger,  # Pass the logger we already created
        )

    def _enqueue(self, payload: Dict[str, Any]) -> int:
        now = time.time()
        data = json.dumps(payload)
        with self._lock:
            self.conn.execute(
                "INSERT INTO queue (payload, status, retry_count, scheduled_at, created_at, updated_at) VALUES (?, 'queued', 0, ?, ?, ?)",
                (data, now, now, now),
            )
            self.conn.commit()
        return self.queued()

    def get_batch(self, max_batch_size: int, *, block: bool = True) -> List[QueueItem]:
        deadline = time.time() + self.batch_interval if block else time.time()
        rows: List[sqlite3.Row] = []
        while len(rows) < max_batch_size:
            remaining = max_batch_size - len(rows)
            with self._lock:
                cur = self.conn.execute(
                    "SELECT * FROM queue WHERE status='queued' AND scheduled_at <= ? ORDER BY id LIMIT ?",
                    (time.time(), remaining),
                )
                fetched = cur.fetchall()
                if fetched:
                    now = time.time()
                    self.conn.executemany(
                        "UPDATE queue SET status='processing', updated_at=? WHERE id=?",
                        [(now, row["id"]) for row in fetched],
                    )
                    self.conn.commit()
                    rows.extend(fetched)
            if len(rows) >= max_batch_size:
                break
            if not block:
                break
            remaining_time = deadline - time.time()
            if remaining_time <= 0:
                break
            time.sleep(min(self.poll_interval, remaining_time))
        if not rows:
            return []
        if self.logger.isEnabledFor(logging.DEBUG):
            ids = ", ".join(str(row["id"]) for row in rows)
            self.logger.debug("Fetched %d messages for processing: %s", len(rows), ids)
        return [
            QueueItem(
                id=row["id"],
                payload=json.loads(row["payload"]),
                retry_count=row["retry_count"],
            )
            for row in rows
        ]

    def acknowledge(self, items: List[QueueItem]) -> None:
        ids = [(item.id,) for item in items if item.id is not None]
        if not ids:
            return
        with self._lock:
            self.conn.executemany("DELETE FROM queue WHERE id=?", ids)
            self.conn.commit()
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Delivered %d messages", len(ids))

    def reschedule(self, item: QueueItem) -> None:
        retry_count = item.retry_count
        if retry_count >= self.max_retries:
            status = "failed"
            scheduled = time.time()
        else:
            status = "queued"
            scheduled = time.time() + min(2**retry_count, 300)
        with self._lock:
            self.conn.execute(
                "UPDATE queue SET status=?, retry_count=?, scheduled_at=?, updated_at=? WHERE id=?",
                (status, retry_count, scheduled, time.time(), item.id),
            )
            self.conn.commit()
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                "Rescheduled message id=%s retry=%s status=%s next_at=%.2f",
                item.id,
                retry_count,
                status,
                scheduled,
            )

    def queued(self) -> int:
        with self._lock:
            cur = self.conn.execute("SELECT COUNT(*) FROM queue WHERE status='queued'")
            (count,) = cur.fetchone()
        return int(count)

    def stop(self) -> None:
        if self._closed:
            return
        super().stop()
        # Capture final statistics before closing the underlying database
        self._final_stats = super().stats()
        self.conn.close()
        self._closed = True

    def stats(self) -> Dict[str, Any]:
        if self._closed and self._final_stats is not None:
            return self._final_stats
        return super().stats()
