import unittest
import threading
import time
from unittest.mock import patch

from spring_pkg.utils.safe_counter import SafeCounter


class TestSafeCounter(unittest.TestCase):
    """Test cases for SafeCounter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.counter = SafeCounter()

    def test_initial_count(self):
        """Test that initial count is zero."""
        self.assertEqual(self.counter.count(), 0)

    def test_increment(self):
        """Test increment functionality."""
        self.counter.increment()
        self.assertEqual(self.counter.count(), 1)
        
        self.counter.increment()
        self.assertEqual(self.counter.count(), 2)

    def test_decrement(self):
        """Test decrement functionality."""
        self.counter.increment()
        self.counter.increment()
        self.assertEqual(self.counter.count(), 2)
        
        self.counter.decrement()
        self.assertEqual(self.counter.count(), 1)
        
        self.counter.decrement()
        self.assertEqual(self.counter.count(), 0)

    def test_decrement_below_zero(self):
        """Test that decrement can go below zero."""
        self.counter.decrement()
        self.assertEqual(self.counter.count(), -1)

    def test_thread_safety(self):
        """Test that SafeCounter is thread-safe."""
        num_threads = 10
        increments_per_thread = 100
        
        def increment_worker():
            for _ in range(increments_per_thread):
                self.counter.increment()
        
        def decrement_worker():
            for _ in range(increments_per_thread // 2):
                self.counter.decrement()
        
        threads = []
        
        # Create increment threads
        for _ in range(num_threads):
            thread = threading.Thread(target=increment_worker)
            threads.append(thread)
        
        # Create decrement threads
        for _ in range(num_threads // 2):
            thread = threading.Thread(target=decrement_worker)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Expected result: 10 threads * 100 increments - 5 threads * 50 decrements
        expected = (num_threads * increments_per_thread) - ((num_threads // 2) * (increments_per_thread // 2))
        self.assertEqual(self.counter.count(), expected)

    def test_concurrent_access(self):
        """Test concurrent read/write access."""
        results = []
        
        def worker():
            for i in range(50):
                self.counter.increment()
                count = self.counter.count()
                results.append(count)
                self.counter.decrement()
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Final count should be 0 (equal increments and decrements)
        self.assertEqual(self.counter.count(), 0)
        # All intermediate results should be valid integers
        self.assertTrue(all(isinstance(result, int) for result in results))

    def test_multiple_increments_decrements(self):
        """Test multiple operations in sequence."""
        operations = [
            ('increment', 1),
            ('increment', 2),
            ('increment', 3),
            ('decrement', 2),
            ('increment', 3),
            ('decrement', 2),
            ('decrement', 1),
            ('decrement', 0),
        ]
        
        for operation, expected in operations:
            if operation == 'increment':
                self.counter.increment()
            else:
                self.counter.decrement()
            self.assertEqual(self.counter.count(), expected)


if __name__ == '__main__':
    unittest.main()
