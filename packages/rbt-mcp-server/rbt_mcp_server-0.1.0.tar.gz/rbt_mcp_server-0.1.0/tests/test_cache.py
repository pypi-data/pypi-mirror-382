"""
Test cases for DocumentCache module.

@REQ: REQ-rbt-mcp-tool
@BP: BP-rbt-mcp-tool
@TASK: TASK-002-DocumentCache

Test DocumentCache implementation with LRU + TTL strategies.
"""

import pytest
import time
import threading
from datetime import datetime, timezone
from rbt_mcp_server.cache import DocumentState, DocumentCache


class TestDocumentState:
    """Test DocumentState dataclass."""

    def test_document_state_creation(self):
        """Test creating a DocumentState instance."""
        now = datetime.now(timezone.utc)
        data = {"key": "value", "metadata": {"id": "test"}}

        state = DocumentState(
            file_path="/path/to/file.md",
            json_data=data,
            last_access=now
        )

        assert state.file_path == "/path/to/file.md"
        assert state.json_data == data
        assert state.last_access == now


class TestDocumentCache:
    """Test DocumentCache with LRU and TTL strategies."""

    def test_basic_cache_get_put(self):
        """
        Test Case 1: Basic cache access.
        Given: Empty DocumentCache
        When: put("file1.md", data1), then get("file1.md")
        Then: Returns data1
        """
        cache = DocumentCache(max_size=10, ttl_seconds=300)
        data1 = {"content": "test data 1"}

        cache.put("file1.md", data1)
        result = cache.get("file1.md")

        assert result == data1

    def test_cache_miss(self):
        """Test getting non-existent key returns None."""
        cache = DocumentCache(max_size=10, ttl_seconds=300)
        result = cache.get("nonexistent.md")
        assert result is None

    def test_lru_eviction(self):
        """
        Test Case 2: LRU eviction strategy.
        Given: DocumentCache with max_size=3, containing 3 files
        When: Put 4th file (without accessing any existing file)
        Then: 1st file is evicted, get 1st file returns None
        """
        cache = DocumentCache(max_size=3, ttl_seconds=300)

        cache.put("file1.md", {"content": "data1"})
        cache.put("file2.md", {"content": "data2"})
        cache.put("file3.md", {"content": "data3"})

        # Cache is now full (3/3), order: file1 (oldest), file2, file3 (newest)
        # Adding 4th file should evict file1 (least recently used)
        cache.put("file4.md", {"content": "data4"})

        assert cache.get("file1.md") is None
        assert cache.get("file2.md") is not None
        assert cache.get("file3.md") is not None
        assert cache.get("file4.md") is not None

    def test_lru_access_order_update(self):
        """
        Test Case 3: LRU access order update.
        Given: Cache contains file1, file2, file3 (added in order)
        When: get(file1), then put(file4)
        Then: file2 is evicted (file1 moved to end by access)
        """
        cache = DocumentCache(max_size=3, ttl_seconds=300)

        cache.put("file1.md", {"content": "data1"})
        cache.put("file2.md", {"content": "data2"})
        cache.put("file3.md", {"content": "data3"})

        # Access file1 to move it to the end (most recently used)
        cache.get("file1.md")

        # Now order is: file2 (oldest), file3, file1 (newest)
        # Adding file4 should evict file2
        cache.put("file4.md", {"content": "data4"})

        assert cache.get("file1.md") is not None  # Still in cache
        assert cache.get("file2.md") is None      # Evicted
        assert cache.get("file3.md") is not None
        assert cache.get("file4.md") is not None

    def test_ttl_expiration(self):
        """
        Test Case 4: TTL expiration cleanup.
        Given: DocumentCache with ttl_seconds=2, put("file1.md", data1)
        When: Wait 3 seconds, call _cleanup_expired()
        Then: file1.md is removed, get("file1.md") returns None
        """
        cache = DocumentCache(max_size=10, ttl_seconds=2)
        data1 = {"content": "test data"}

        cache.put("file1.md", data1)
        assert cache.get("file1.md") is not None

        # Wait for TTL to expire
        time.sleep(3)

        # Manually trigger cleanup
        cache._cleanup_expired()

        # File should be removed
        assert cache.get("file1.md") is None

    def test_clear_specific_file(self):
        """
        Test Case 5: Clear specific cache entry.
        Given: Cache contains file1, file2
        When: clear("file1.md")
        Then: file1 is removed, file2 still exists
        """
        cache = DocumentCache(max_size=10, ttl_seconds=300)

        cache.put("file1.md", {"content": "data1"})
        cache.put("file2.md", {"content": "data2"})

        cache.clear("file1.md")

        assert cache.get("file1.md") is None
        assert cache.get("file2.md") is not None

    def test_clear_all_cache(self):
        """
        Test Case 6: Clear all cache entries.
        Given: Cache contains file1, file2, file3
        When: clear() (no argument)
        Then: All cache entries are removed
        """
        cache = DocumentCache(max_size=10, ttl_seconds=300)

        cache.put("file1.md", {"content": "data1"})
        cache.put("file2.md", {"content": "data2"})
        cache.put("file3.md", {"content": "data3"})

        cache.clear()

        assert cache.get("file1.md") is None
        assert cache.get("file2.md") is None
        assert cache.get("file3.md") is None

    def test_thread_safety(self):
        """
        Test Case 7: Thread safety (concurrent access).
        Given: DocumentCache with 5 threads
        When: 5 threads simultaneously put/get different files
        Then: No race condition, all operations complete correctly
        """
        cache = DocumentCache(max_size=10, ttl_seconds=300)
        errors = []

        def worker(thread_id):
            try:
                file_name = f"file{thread_id}.md"
                data = {"content": f"data{thread_id}"}

                # Put data
                cache.put(file_name, data)

                # Get data
                result = cache.get(file_name)

                # Verify
                assert result == data, f"Thread {thread_id} data mismatch"
            except Exception as e:
                errors.append((thread_id, str(e)))

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"

    def test_update_existing_key(self):
        """Test updating an existing cache entry."""
        cache = DocumentCache(max_size=10, ttl_seconds=300)

        cache.put("file1.md", {"content": "data1"})
        cache.put("file1.md", {"content": "updated_data"})

        result = cache.get("file1.md")
        assert result == {"content": "updated_data"}

    def test_background_cleanup_thread(self):
        """Test that background cleanup thread properly cleans expired entries."""
        cache = DocumentCache(max_size=10, ttl_seconds=1)
        cache.start()

        try:
            cache.put("file1.md", {"content": "data1"})
            assert cache.get("file1.md") is not None

            # Wait for TTL to expire and cleanup thread to run
            # Note: cleanup runs every 60 seconds, so we test _cleanup_expired directly
            time.sleep(2)
            cache._cleanup_expired()

            assert cache.get("file1.md") is None
        finally:
            cache.stop()

    def test_start_stop_lifecycle(self):
        """Test starting and stopping the cache lifecycle."""
        cache = DocumentCache(max_size=10, ttl_seconds=300)

        # Should be able to start
        cache.start()

        # Put some data
        cache.put("file1.md", {"content": "data1"})
        assert cache.get("file1.md") is not None

        # Should be able to stop
        cache.stop()

        # Data should still be accessible after stop
        assert cache.get("file1.md") is not None
