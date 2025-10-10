import unittest
import threading
import time
import logging
import io
from unittest.mock import patch, MagicMock

from spring_pkg.requests.counter import message_counter, get_count, wait_for_empty, _mq_count
from spring_pkg.requests.stream_logger import StreamLogger


class TestMessageCounter(unittest.TestCase):
    """Test cases for message counter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset counter before each test
        with _mq_count['lock']:
            _mq_count['count'] = 0

    def tearDown(self):
        """Clean up after tests."""
        # Reset counter after each test
        with _mq_count['lock']:
            _mq_count['count'] = 0

    def test_initial_count(self):
        """Test that initial count is zero."""
        self.assertEqual(get_count(), 0)

    def test_message_counter_decorator(self):
        """Test message_counter decorator functionality."""
        @message_counter
        def test_function():
            return "test_result"
        
        # Count should be 0 initially
        self.assertEqual(get_count(), 0)
        
        # Call the decorated function
        result = test_function()
        
        # Function should return correct result
        self.assertEqual(result, "test_result")
        
        # Count should be back to 0 after function completes
        self.assertEqual(get_count(), 0)

    def test_message_counter_increments_during_execution(self):
        """Test that counter increments during function execution."""
        counts_during_execution = []
        
        @message_counter
        def test_function():
            counts_during_execution.append(get_count())
            time.sleep(0.1)  # Simulate some work
            counts_during_execution.append(get_count())
            return "done"
        
        result = test_function()
        
        self.assertEqual(result, "done")
        # During execution, count should have been 1
        self.assertEqual(counts_during_execution[0], 1)
        self.assertEqual(counts_during_execution[1], 1)
        # After execution, count should be 0
        self.assertEqual(get_count(), 0)

    def test_message_counter_with_exception(self):
        """Test message_counter decorator when function raises exception."""
        @message_counter
        def failing_function():
            raise ValueError("Test error")
        
        self.assertEqual(get_count(), 0)
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Count should be reset to 0 even after exception
        self.assertEqual(get_count(), 0)

    def test_multiple_concurrent_functions(self):
        """Test multiple functions running concurrently."""
        max_count_seen = 0
        lock = threading.Lock()
        
        @message_counter
        def worker_function(duration):
            nonlocal max_count_seen
            time.sleep(duration)
            with lock:
                current_count = get_count()
                if current_count > max_count_seen:
                    max_count_seen = current_count
        
        # Start 5 threads with different durations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_function, args=(0.1 + i * 0.02,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # All functions should have completed
        self.assertEqual(get_count(), 0)
        # At some point, we should have seen multiple functions running
        self.assertGreater(max_count_seen, 1)

    def test_message_counter_with_args_kwargs(self):
        """Test message_counter with function arguments."""
        @message_counter
        def function_with_args(a, b, c=None, d="default"):
            return {"a": a, "b": b, "c": c, "d": d}
        
        result = function_with_args(1, 2, c=3, d="custom")
        expected = {"a": 1, "b": 2, "c": 3, "d": "custom"}
        
        self.assertEqual(result, expected)
        self.assertEqual(get_count(), 0)

    def test_negative_count_protection(self):
        """Test that count doesn't go below zero."""
        # Manually decrement count to simulate edge case
        with _mq_count['lock']:
            _mq_count['count'] = -5
        
        @message_counter
        def test_function():
            return "test"
        
        result = test_function()
        self.assertEqual(result, "test")
        
        # Count should be reset to 0, not go more negative
        self.assertEqual(get_count(), 0)


class TestStreamLogger(unittest.TestCase):
    """Test cases for StreamLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = StreamLogger("test_logger")

    def test_stream_logger_initialization(self):
        """Test StreamLogger initialization."""
        logger = StreamLogger("test", logging.INFO)
        self.assertEqual(logger.name, "test")
        self.assertEqual(logger.level, logging.INFO)
        self.assertFalse(logger.propagate)

    def test_log_message_capture(self):
        """Test that StreamLogger captures log messages."""
        self.logger.info("Test info message")
        self.logger.warning("Test warning message")
        
        content = self.logger.report()
        
        self.assertIn("Test info message", content)
        self.assertIn("Test warning message", content)
        self.assertIn("INFO", content)
        self.assertIn("WARNING", content)

    def test_highest_level_tracking(self):
        """Test that StreamLogger tracks highest log level."""
        self.assertEqual(self.logger.highest_level, logging.NOTSET)
        
        self.logger.debug("Debug message")
        self.assertEqual(self.logger.highest_level, logging.DEBUG)
        
        self.logger.info("Info message")
        self.assertEqual(self.logger.highest_level, logging.INFO)
        
        self.logger.error("Error message")
        self.assertEqual(self.logger.highest_level, logging.ERROR)
        
        # Adding a lower level shouldn't change highest level
        self.logger.warning("Warning message")
        self.assertEqual(self.logger.highest_level, logging.ERROR)

    def test_report_with_standard_logger(self):
        """Test report method with standard logger."""
        self.logger.error("Test error message")
        
        # Create a mock standard logger
        mock_logger = MagicMock()
        
        content = self.logger.report(mock_logger)
        
        # Should have called log with ERROR level
        mock_logger.log.assert_called_once_with(logging.ERROR, content)
        self.assertIn("Test error message", content)

    def test_report_without_standard_logger(self):
        """Test report method without providing standard logger."""
        self.logger.warning("Test warning")
        
        with patch('logging.getLogger') as mock_get_logger:
            mock_standard_logger = MagicMock()
            mock_get_logger.return_value = mock_standard_logger
            
            content = self.logger.report()
            
            mock_get_logger.assert_called_once_with()
            mock_standard_logger.log.assert_called_once_with(logging.WARNING, content)

    def test_empty_report(self):
        """Test report when no messages were logged."""
        content = self.logger.report()
        self.assertEqual(content, "")

    def test_multiple_reports(self):
        """Test multiple calls to report."""
        self.logger.info("First message")
        first_content = self.logger.report()
        
        self.logger.warning("Second message")
        second_content = self.logger.report()
        
        # Both reports should contain all messages
        self.assertIn("First message", first_content)
        self.assertIn("First message", second_content)
        self.assertIn("Second message", second_content)

    def test_log_formatting(self):
        """Test that log messages are properly formatted."""
        self.logger.info("Test message")
        content = self.logger.report()
        
        # Should contain timestamp, level, and message
        self.assertIn("INFO", content)
        self.assertIn("Test message", content)
        # Should contain some timestamp format
        self.assertTrue(any(char.isdigit() for char in content))

    def test_different_log_levels(self):
        """Test logging at different levels."""
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        
        content = self.logger.report()
        
        # All messages should be captured
        self.assertIn("Debug message", content)
        self.assertIn("Info message", content)
        self.assertIn("Warning message", content)
        self.assertIn("Error message", content)
        self.assertIn("Critical message", content)
        
        # Highest level should be CRITICAL
        self.assertEqual(self.logger.highest_level, logging.CRITICAL)

    def test_stream_logger_isolation(self):
        """Test that multiple StreamLogger instances are isolated."""
        logger1 = StreamLogger("logger1")
        logger2 = StreamLogger("logger2")
        
        logger1.info("Message from logger1")
        logger2.warning("Message from logger2")
        
        content1 = logger1.report()
        content2 = logger2.report()
        
        self.assertIn("Message from logger1", content1)
        self.assertNotIn("Message from logger2", content1)
        
        self.assertIn("Message from logger2", content2)
        self.assertNotIn("Message from logger1", content2)


if __name__ == '__main__':
    unittest.main()
