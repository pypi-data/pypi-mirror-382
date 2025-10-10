import unittest
import threading
import time
import tempfile
import os
from unittest.mock import patch, mock_open, MagicMock

from spring_pkg.monitor.memory_watch import (
    MemoryUsage, MemWatchAlert, MemWatch, 
    get_memory_usage, hist_memory_max, add_threshold,
    start_memory_watch, stop_memory_watch,
    _mem_report, _memory_watch_procedure
)
from spring_pkg.monitor.thread_db import (
    get_thread_record, get_live_threads, save_thread_data, get_thread_data,
    _get_ident, _get_thread_ident, lck, data
)


class TestMemoryUsage(unittest.TestCase):
    """Test cases for MemoryUsage dataclass."""

    def test_memory_usage_creation(self):
        """Test MemoryUsage dataclass creation."""
        mem_usage = MemoryUsage(percent=75, rss=1024000, swap=512000, total=2048000)
        
        self.assertEqual(mem_usage.percent, 75)
        self.assertEqual(mem_usage.rss, 1024000)
        self.assertEqual(mem_usage.swap, 512000)
        self.assertEqual(mem_usage.total, 2048000)


class TestMemWatchAlert(unittest.TestCase):
    """Test cases for MemWatchAlert dataclass."""

    def test_mem_watch_alert_creation(self):
        """Test MemWatchAlert dataclass creation."""
        alert = MemWatchAlert(
            direction=1,
            percent=80,
            triggered=False,
            check_interval=5.0,
            notification_name="memory-warning"
        )
        
        self.assertEqual(alert.direction, 1)
        self.assertEqual(alert.percent, 80)
        self.assertFalse(alert.triggered)
        self.assertEqual(alert.check_interval, 5.0)
        self.assertEqual(alert.notification_name, "memory-warning")


class TestMemWatch(unittest.TestCase):
    """Test cases for MemWatch functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset MemWatch state
        with MemWatch.lock:
            MemWatch.running = False
            MemWatch.stop_requested = False
            MemWatch.thread = None
            MemWatch.limits.clear()
            MemWatch.hist_max = 0

    def tearDown(self):
        """Clean up after tests."""
        # Ensure memory watch is stopped
        if MemWatch.is_running():
            stop_memory_watch()
        
        # Reset state
        with MemWatch.lock:
            MemWatch.running = False
            MemWatch.stop_requested = False
            MemWatch.thread = None
            MemWatch.limits.clear()
            MemWatch.hist_max = 0

    def test_is_running_initial_state(self):
        """Test initial running state."""
        self.assertFalse(MemWatch.is_running())

    def test_is_stop_requested_initial_state(self):
        """Test initial stop requested state."""
        self.assertFalse(MemWatch.is_stop_requested())

    def test_add_threshold(self):
        """Test adding memory thresholds."""
        add_threshold(1, 80, 5.0, "warning")
        add_threshold(-1, 70, 3.0, "info")
        
        with MemWatch.lock:
            self.assertEqual(len(MemWatch.limits), 2)
            
            # Check that limits are sorted
            self.assertEqual(MemWatch.limits[0].direction, -1)
            self.assertEqual(MemWatch.limits[1].direction, 1)

    def test_clear_trigger_above(self):
        """Test clearing triggers above a threshold."""
        add_threshold(1, 80, 5.0, "warning1")
        add_threshold(1, 90, 5.0, "warning2")
        add_threshold(1, 95, 5.0, "warning3")
        
        # Trigger all alerts
        with MemWatch.lock:
            for alert in MemWatch.limits:
                alert.triggered = True
        
        # Clear triggers above 85%
        MemWatch.clear_trigger_above(85)
        
        with MemWatch.lock:
            # 80% alert should still be triggered
            self.assertTrue(MemWatch.limits[0].triggered)
            # 90% and 95% alerts should be cleared
            self.assertFalse(MemWatch.limits[1].triggered)
            self.assertFalse(MemWatch.limits[2].triggered)

    def test_find_trigger_up(self):
        """Test finding upward triggers."""
        add_threshold(1, 80, 5.0, "warning")
        
        alert_up, alert_down = MemWatch.find_trigger(75, 85)
        
        self.assertIsNotNone(alert_up)
        self.assertIsNone(alert_down)
        self.assertEqual(alert_up.percent, 80)

    def test_find_trigger_down(self):
        """Test finding downward triggers."""
        add_threshold(-1, 80, 5.0, "info")
        
        alert_up, alert_down = MemWatch.find_trigger(85, 75)
        
        self.assertIsNone(alert_up)
        self.assertIsNotNone(alert_down)
        self.assertEqual(alert_down.percent, 80)

    def test_find_trigger_no_trigger(self):
        """Test when no triggers are found."""
        add_threshold(1, 80, 5.0, "warning")
        
        # No threshold crossed
        alert_up, alert_down = MemWatch.find_trigger(75, 78)
        
        self.assertIsNone(alert_up)
        self.assertIsNone(alert_down)

    @patch('spring_pkg.monitor.memory_watch.send')
    def test_mem_report(self, mock_send):
        """Test memory report function."""
        _mem_report("test-notification", "Test message")
        mock_send.assert_called_once_with("test-notification", "Test message")

    @patch('builtins.open', mock_open(read_data="""rss 1048576
swap 524288
hierarchical_memsw_limit 2097152
other_field 12345"""))
    def test_get_memory_usage(self):
        """Test get_memory_usage function."""
        usage = get_memory_usage()
        
        self.assertIsInstance(usage, MemoryUsage)
        self.assertEqual(usage.rss, 1048576)
        self.assertEqual(usage.swap, 524288)
        self.assertEqual(usage.total, 2097152)
        # percent should be calculated correctly: (1048576 + 524288) / 2097152 * 100 = 75
        self.assertEqual(usage.percent, 75)

    def test_hist_memory_max_units(self):
        """Test hist_memory_max with different units."""
        MemWatch.hist_max = 1048576  # 1 MB
        
        self.assertEqual(hist_memory_max('B'), '1048576 B')
        self.assertEqual(hist_memory_max('KB'), '1024 KB')
        self.assertEqual(hist_memory_max('MB'), '1 MB')
        self.assertEqual(hist_memory_max('GB'), '0.0009765625 GB')
        
        # Default should be MB
        self.assertEqual(hist_memory_max(), '1 MB')


class TestThreadDB(unittest.TestCase):
    """Test cases for thread database functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear thread data before each test
        with lck:
            data.clear()

    def tearDown(self):
        """Clean up after tests."""
        # Clear thread data after each test
        with lck:
            data.clear()

    def test_get_thread_record(self):
        """Test getting thread record."""
        record = get_thread_record()
        
        # Should return a dictionary
        self.assertIsInstance(record, dict)
        
        # Should be empty initially
        self.assertEqual(len(record), 0)

    def test_save_and_get_thread_data(self):
        """Test saving and retrieving thread data."""
        save_thread_data("test_key", "test_value")
        
        value = get_thread_data("test_key")
        self.assertEqual(value, "test_value")

    def test_get_thread_data_default(self):
        """Test getting thread data with default value."""
        value = get_thread_data("nonexistent_key", "default_value")
        self.assertEqual(value, "default_value")

    def test_get_thread_data_empty_default(self):
        """Test getting thread data with default empty string."""
        value = get_thread_data("nonexistent_key")
        self.assertEqual(value, "")

    def test_thread_data_isolation(self):
        """Test that thread data is isolated between threads."""
        results = {}
        
        def worker(thread_id):
            save_thread_data("thread_id", thread_id)
            save_thread_data("data", f"data_for_{thread_id}")
            
            # Small delay to ensure threads don't interfere
            time.sleep(0.1)
            
            retrieved_id = get_thread_data("thread_id")
            retrieved_data = get_thread_data("data")
            
            results[thread_id] = {
                "id": retrieved_id,
                "data": retrieved_data
            }
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(f"thread_{i}",))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Each thread should have its own data
        for i in range(3):
            thread_id = f"thread_{i}"
            self.assertEqual(results[thread_id]["id"], thread_id)
            self.assertEqual(results[thread_id]["data"], f"data_for_{thread_id}")

    def test_get_live_threads(self):
        """Test getting live threads."""
        # Add some correlation IDs to current and other threads
        save_thread_data("correlationId", "main_thread_correlation")
        
        def worker():
            save_thread_data("correlationId", "worker_thread_correlation")
            save_thread_data("other_data", "worker_data")
            time.sleep(0.5)  # Keep thread alive for test
        
        thread = threading.Thread(target=worker)
        thread.start()
        
        # Wait for worker to set data
        time.sleep(0.1)
        
        live_threads = get_live_threads()
        
        # Should have at least one thread with correlation ID
        self.assertGreater(len(live_threads), 0)
        
        # Check that correlation IDs are present
        correlation_ids = [data.get("correlationId") for data in live_threads.values()]
        self.assertIn("main_thread_correlation", correlation_ids)
        
        thread.join()

    def test_thread_record_persistence(self):
        """Test that thread record persists across calls."""
        # Set some data
        save_thread_data("key1", "value1")
        save_thread_data("key2", "value2")
        
        # Get record again
        record1 = get_thread_record()
        record2 = get_thread_record()
        
        # Should be the same record
        self.assertIs(record1, record2)
        self.assertEqual(record1["key1"], "value1")
        self.assertEqual(record2["key2"], "value2")

    def test_get_ident_function(self):
        """Test _get_ident function."""
        ident = _get_ident()
        self.assertIsInstance(ident, int)
        self.assertGreater(ident, 0)

    def test_get_thread_ident_function(self):
        """Test _get_thread_ident function."""
        current_thread = threading.current_thread()
        ident = _get_thread_ident(current_thread)
        
        self.assertIsInstance(ident, int)
        self.assertGreater(ident, 0)

    def test_concurrent_thread_data_access(self):
        """Test concurrent access to thread data."""
        results = []
        
        def worker(worker_id):
            for i in range(10):
                save_thread_data(f"key_{i}", f"worker_{worker_id}_value_{i}")
                retrieved = get_thread_data(f"key_{i}")
                results.append((worker_id, i, retrieved))
                time.sleep(0.01)
        
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker, args=(worker_id,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All results should be correct
        for worker_id, key_index, retrieved in results:
            expected = f"worker_{worker_id}_value_{key_index}"
            self.assertEqual(retrieved, expected)


if __name__ == '__main__':
    unittest.main()
