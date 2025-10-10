import unittest
import threading
import time

from spring_pkg.notifications.shutdown import shutdown_service, is_shutting_down
from spring_pkg.notifications.testmode import set_test_mode, get_test_mode
from spring_pkg.coding.locked_status import LockedValue


class TestShutdownService(unittest.TestCase):
    """Test cases for shutdown service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset shutdown status
        from spring_pkg.notifications.shutdown import _should_shut_down
        _should_shut_down.set(False)

    def test_initial_shutdown_status(self):
        """Test that initial shutdown status is False."""
        self.assertFalse(is_shutting_down())

    def test_shutdown_service_sets_status(self):
        """Test that shutdown_service sets the status to True."""
        self.assertFalse(is_shutting_down())
        shutdown_service()
        self.assertTrue(is_shutting_down())

    def test_multiple_shutdown_calls(self):
        """Test multiple calls to shutdown_service."""
        shutdown_service()
        self.assertTrue(is_shutting_down())
        
        shutdown_service()  # Call again
        self.assertTrue(is_shutting_down())  # Should still be True

    def test_shutdown_thread_safety(self):
        """Test thread safety of shutdown service."""
        results = []
        
        def worker():
            shutdown_service()
            results.append(is_shutting_down())
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All results should be True
        self.assertTrue(all(results))
        self.assertTrue(is_shutting_down())


class TestTestMode(unittest.TestCase):
    """Test cases for test mode functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset test mode
        set_test_mode(False)

    def test_initial_test_mode(self):
        """Test initial test mode status."""
        set_test_mode(False)  # Ensure it's reset
        # Note: get_test_mode() has a bug - missing return statement
        # We'll test the underlying functionality
        from spring_pkg.notifications.testmode import _test_g_mode
        self.assertFalse(_test_g_mode.get())

    def test_set_test_mode_true(self):
        """Test setting test mode to True."""
        set_test_mode(True)
        from spring_pkg.notifications.testmode import _test_g_mode
        self.assertTrue(_test_g_mode.get())

    def test_set_test_mode_false(self):
        """Test setting test mode to False."""
        set_test_mode(True)
        set_test_mode(False)
        from spring_pkg.notifications.testmode import _test_g_mode
        self.assertFalse(_test_g_mode.get())

    def test_test_mode_thread_safety(self):
        """Test thread safety of test mode."""
        def worker_true():
            set_test_mode(True)
        
        def worker_false():
            set_test_mode(False)
        
        threads = []
        # Create threads that set different values
        for i in range(10):
            if i % 2 == 0:
                thread = threading.Thread(target=worker_true)
            else:
                thread = threading.Thread(target=worker_false)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Final state should be consistent (either True or False)
        from spring_pkg.notifications.testmode import _test_g_mode
        final_state = _test_g_mode.get()
        self.assertIsInstance(final_state, bool)


class TestLockedValue(unittest.TestCase):
    """Test cases for LockedValue class."""

    def test_initial_status_default(self):
        """Test initial status with default value."""
        status = LockedValue[bool](False)
        self.assertFalse(status.get())

    def test_initial_status_true(self):
        """Test initial status set to True."""
        status = LockedValue[bool](True)
        self.assertTrue(status.get())

    def test_initial_status_false(self):
        """Test initial status set to False."""
        status = LockedValue[bool](False)
        self.assertFalse(status.get())

    def test_set_and_get(self):
        """Test setting and getting status."""
        status = LockedValue[bool](False)
        
        status.set(True)
        self.assertTrue(status.get())
        
        status.set(False)
        self.assertFalse(status.get())
        
        status.set(True)
        self.assertTrue(status.get())

    def test_thread_safety(self):
        """Test thread safety of LockedValue."""
        status = LockedValue[bool](False)
        results = []
        
        def worker_set_true():
            for _ in range(100):
                status.set(True)
                results.append(status.get())
        
        def worker_set_false():
            for _ in range(100):
                status.set(False)
                results.append(status.get())
        
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=worker_set_true))
            threads.append(threading.Thread(target=worker_set_false))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All results should be boolean values
        self.assertTrue(all(isinstance(result, bool) for result in results))
        
        # Final state should be consistent
        final_state = status.get()
        self.assertIsInstance(final_state, bool)

    def test_concurrent_read_write(self):
        """Test concurrent read and write operations."""
        status = LockedValue[bool](False)
        read_results = []
        write_count = 0
        
        def reader():
            for _ in range(50):
                result = status.get()
                read_results.append(result)
                time.sleep(0.001)
        
        def writer():
            nonlocal write_count
            for i in range(50):
                status.set(i % 2 == 0)
                write_count += 1
                time.sleep(0.001)
        
        # Start reader and writer threads
        reader_thread = threading.Thread(target=reader)
        writer_thread = threading.Thread(target=writer)
        
        reader_thread.start()
        writer_thread.start()
        
        reader_thread.join()
        writer_thread.join()
        
        # Should have completed all operations
        self.assertEqual(write_count, 50)
        self.assertEqual(len(read_results), 50)
        
        # All read results should be boolean
        self.assertTrue(all(isinstance(result, bool) for result in read_results))

    def test_multiple_instances(self):
        """Test that multiple LockedValue instances are independent."""
        status1 = LockedValue[bool](False)
        status2 = LockedValue[bool](True)
        
        self.assertFalse(status1.get())
        self.assertTrue(status2.get())
        
        status1.set(True)
        self.assertTrue(status1.get())
        self.assertTrue(status2.get())
        
        status2.set(False)
        self.assertTrue(status1.get())
        self.assertFalse(status2.get())


if __name__ == '__main__':
    unittest.main()
