import unittest
import threading
import time
from unittest.mock import patch, MagicMock

from spring_pkg.utils.waitloop import waitloop_start, waitloop_is_at_exit, signal_exit


class TestWaitloop(unittest.TestCase):
    """Test cases for waitloop functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset the signal_exit event before each test
        signal_exit.clear()

    def tearDown(self):
        """Clean up after tests."""
        # Ensure signal_exit is cleared after each test
        signal_exit.clear()

    def test_waitloop_is_at_exit_initial_state(self):
        """Test that waitloop_is_at_exit returns False initially."""
        self.assertFalse(waitloop_is_at_exit())

    def test_waitloop_is_at_exit_after_signal(self):
        """Test that waitloop_is_at_exit returns True after signal is set."""
        signal_exit.set()
        self.assertTrue(waitloop_is_at_exit())

    @patch('spring_pkg.utils.waitloop.send')
    @patch('time.sleep')
    def test_waitloop_start_keyboard_interrupt(self, mock_sleep, mock_send):
        """Test waitloop_start handles KeyboardInterrupt correctly."""
        # Simulate KeyboardInterrupt after first sleep
        mock_sleep.side_effect = KeyboardInterrupt()
        
        waitloop_start()
        
        # Check that send was called with correct parameters
        mock_send.assert_called_once_with('waitloop-did-finish', {'reason': 'KeyboardInterrupt'})
        
        # Check that signal_exit is set
        self.assertTrue(signal_exit.is_set())

    @patch('spring_pkg.utils.waitloop.send')
    @patch('time.sleep')
    def test_waitloop_start_multiple_sleeps_then_interrupt(self, mock_sleep, mock_send):
        """Test waitloop_start with multiple sleeps before KeyboardInterrupt."""
        # Sleep normally twice, then raise KeyboardInterrupt
        sleep_count = 0
        def sleep_side_effect(duration):
            nonlocal sleep_count
            sleep_count += 1
            if sleep_count >= 3:
                raise KeyboardInterrupt()
        
        mock_sleep.side_effect = sleep_side_effect
        
        waitloop_start()
        
        # Should have called sleep 3 times
        self.assertEqual(mock_sleep.call_count, 3)
        
        # Should have sent notification
        mock_send.assert_called_once_with('waitloop-did-finish', {'reason': 'KeyboardInterrupt'})
        
        # Signal should be set
        self.assertTrue(signal_exit.is_set())

    def test_signal_exit_thread_safety(self):
        """Test that signal_exit works correctly across threads."""
        results = []
        
        def check_exit_status():
            results.append(waitloop_is_at_exit())
        
        # Start with signal not set
        self.assertFalse(waitloop_is_at_exit())
        
        # Create threads to check status
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=check_exit_status)
            threads.append(thread)
        
        # Start threads
        for thread in threads:
            thread.start()
        
        # Wait a bit then set signal
        time.sleep(0.1)
        signal_exit.set()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # All results should be False (signal was not set when threads ran)
        self.assertTrue(all(result is False for result in results))
        
        # But now it should be True
        self.assertTrue(waitloop_is_at_exit())

    @patch('time.sleep')
    def test_waitloop_start_infinite_loop_behavior(self, mock_sleep):
        """Test that waitloop_start creates an infinite loop until interrupted."""
        call_count = 0
        
        def sleep_side_effect(duration):
            nonlocal call_count
            call_count += 1
            if call_count >= 10:  # Stop after 10 iterations
                raise KeyboardInterrupt()
            self.assertEqual(duration, 1)  # Should always sleep for 1 second
        
        mock_sleep.side_effect = sleep_side_effect
        
        # This should not raise an exception and should exit cleanly
        waitloop_start()
        
        # Should have called sleep 10 times
        self.assertEqual(call_count, 10)

    def test_signal_exit_persistence(self):
        """Test that signal_exit remains set once triggered."""
        # Initially not set
        self.assertFalse(waitloop_is_at_exit())
        
        # Set the signal
        signal_exit.set()
        
        # Should remain True
        self.assertTrue(waitloop_is_at_exit())
        self.assertTrue(waitloop_is_at_exit())  # Multiple calls
        self.assertTrue(waitloop_is_at_exit())

    def test_multiple_threads_checking_exit(self):
        """Test multiple threads checking exit status simultaneously."""
        num_threads = 20
        results = [False] * num_threads
        
        def worker(index):
            # Each thread checks the status multiple times
            for _ in range(10):
                results[index] = waitloop_is_at_exit()
                time.sleep(0.01)
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait a moment, then set signal
        time.sleep(0.05)
        signal_exit.set()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # At least some results should be True (after signal was set)
        # But we can't guarantee all will be True due to timing
        final_check = waitloop_is_at_exit()
        self.assertTrue(final_check)


if __name__ == '__main__':
    unittest.main()
