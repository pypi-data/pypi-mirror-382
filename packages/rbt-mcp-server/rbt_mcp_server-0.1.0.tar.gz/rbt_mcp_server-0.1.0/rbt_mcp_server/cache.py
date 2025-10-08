"""
Document cache management with hybrid LRU + TTL strategy.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-002-DocumentCache

Provides DocumentCache class that manages document JSON cache lifecycle
with LRU eviction (max 10 documents) and TTL expiration (5 minutes).
"""

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional


@dataclass
class DocumentState:
    """
    Document cache state.

    Attributes:
        file_path: Absolute path to the document file
        json_data: Parsed JSON data of the document
        last_access: Last access timestamp (UTC)

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-002-DocumentCache
    """
    file_path: str
    json_data: Dict[str, Any]
    last_access: datetime


class DocumentCache:
    """
    Document cache manager with hybrid LRU + TTL strategy.

    Features:
    - LRU eviction: When cache is full (max_size), evicts least recently used
    - TTL expiration: Background thread cleans up entries older than ttl_seconds
    - Thread-safe: All operations are protected by lock
    - Manual clear: Support clearing specific file or all cache

    @REQ: REQ-rbt-mcp-tool
    @BP: BP-rbt-mcp-tool
    @TASK: TASK-002-DocumentCache
    """

    def __init__(self, max_size: int = 10, ttl_seconds: int = 300):
        """
        Initialize DocumentCache.

        Args:
            max_size: Maximum number of documents to cache (default: 10)
            ttl_seconds: Time-to-live in seconds (default: 300 = 5 minutes)
        """
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, DocumentState] = OrderedDict()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._cleanup_thread: Optional[threading.Thread] = None

    def get(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached document data.

        Updates last_access timestamp and moves entry to end (most recently used).

        Args:
            file_path: File path to look up

        Returns:
            JSON data if found, None otherwise

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        with self._lock:
            if file_path not in self._cache:
                return None

            # Update last access time
            state = self._cache[file_path]
            state.last_access = datetime.now(timezone.utc)

            # Move to end (most recently used)
            self._cache.move_to_end(file_path)

            return state.json_data

    def put(self, file_path: str, json_data: Dict[str, Any]) -> None:
        """
        Put document data into cache.

        If cache is full, evicts least recently used entry (LRU).
        If key exists, updates data and moves to end.

        Args:
            file_path: File path as cache key
            json_data: Document JSON data to cache

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        with self._lock:
            now = datetime.now(timezone.utc)

            # If key exists, update and move to end
            if file_path in self._cache:
                self._cache[file_path].json_data = json_data
                self._cache[file_path].last_access = now
                self._cache.move_to_end(file_path)
            else:
                # Check if cache is full
                if len(self._cache) >= self._max_size:
                    # Remove least recently used (first item)
                    self._cache.popitem(last=False)

                # Add new entry
                state = DocumentState(
                    file_path=file_path,
                    json_data=json_data,
                    last_access=now
                )
                self._cache[file_path] = state

    def clear(self, file_path: Optional[str] = None) -> None:
        """
        Clear cache entries.

        Args:
            file_path: If provided, clear only this file; if None, clear all

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        with self._lock:
            if file_path is None:
                self._cache.clear()
            elif file_path in self._cache:
                del self._cache[file_path]

    def _cleanup_expired(self) -> None:
        """
        Remove expired cache entries based on TTL.

        Removes entries where (now - last_access) > ttl_seconds.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            ttl_delta = timedelta(seconds=self._ttl_seconds)

            # Find expired entries
            expired_keys = [
                file_path
                for file_path, state in self._cache.items()
                if now - state.last_access > ttl_delta
            ]

            # Remove expired entries
            for key in expired_keys:
                del self._cache[key]

    def _cleanup_loop(self) -> None:
        """
        Background thread loop for periodic cleanup.

        Runs every 60 seconds until stop_event is set.

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        while not self._stop_event.is_set():
            # Wait for 60 seconds or until stop event
            if self._stop_event.wait(timeout=60):
                break
            self._cleanup_expired()

    def start(self) -> None:
        """
        Start the background cleanup thread.

        Safe to call multiple times (won't start duplicate threads).

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._stop_event.clear()
            self._cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                daemon=True,
                name="DocumentCache-Cleanup"
            )
            self._cleanup_thread.start()

    def stop(self) -> None:
        """
        Stop the background cleanup thread.

        Blocks until thread terminates (with 5 second timeout).

        @REQ: REQ-rbt-mcp-tool
        @BP: BP-rbt-mcp-tool
        @TASK: TASK-002-DocumentCache
        """
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._stop_event.set()
            self._cleanup_thread.join(timeout=5)
            self._cleanup_thread = None
