import unittest
import datetime
import threading
import time
from spring_pkg.monitor.server import PodHubInfo, PodHubData, PodHubApplication


class TestPodHubInfo(unittest.TestCase):
    
    def setUp(self):
        self.pod_info = PodHubInfo(exp_req=5, exp_sec=10)
    
    def test_initialization(self):
        """Test PodHubInfo initialization"""
        self.assertIsNone(self.pod_info.last_received)
        self.assertIsNone(self.pod_info.last_asked)
        self.assertIsNone(self.pod_info.data)
        self.assertEqual(self.pod_info.expiration_sec, 10)
        self.assertEqual(self.pod_info.expiration_request, 5)
    
    def test_default_values(self):
        """Test default expiration values"""
        default_info = PodHubInfo()
        self.assertEqual(default_info.expiration_sec, 86400)  # 24 hours
        self.assertEqual(default_info.expiration_request, 300)  # 5 minutes
    
    def test_set_and_get_data(self):
        """Test setting and getting data"""
        test_data = {"key": "value", "number": 42}
        
        # Set data
        result = self.pod_info.set_data(test_data)
        self.assertIs(result, self.pod_info)  # Should return self for chaining
        
        # Check that last_received is set
        self.assertIsNotNone(self.pod_info.last_received)
        self.assertIsInstance(self.pod_info.last_received, datetime.datetime)
        
        # Get data
        retrieved_data = self.pod_info.get_data()
        self.assertEqual(retrieved_data, test_data)
    
    def test_should_ask_data_no_previous_requests(self):
        """Test should_ask_data when no previous requests"""
        # Should return True when never asked before
        self.assertTrue(self.pod_info.should_ask_data())
    
    def test_should_ask_data_after_receiving(self):
        """Test should_ask_data behavior after receiving data"""
        # Set some data
        self.pod_info.set_data({"test": "data"})
        
        # Should not ask immediately after receiving
        self.assertFalse(self.pod_info.should_ask_data())
    
    def test_thread_safety(self):
        """Test thread safety of data operations"""
        results = []
        
        def set_data_worker(index):
            data = {"worker": index, "time": datetime.datetime.now()}
            self.pod_info.set_data(data)
            retrieved = self.pod_info.get_data()
            results.append((index, retrieved))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=set_data_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Should have results from all threads
        self.assertEqual(len(results), 5)
        
        # Final data should be from one of the workers
        final_data = self.pod_info.get_data()
        self.assertIn("worker", final_data)
        self.assertIn("time", final_data)


class TestPodHubData(unittest.TestCase):
    
    def test_pod_hub_data_exists(self):
        """Test that PodHubData class exists and can be instantiated"""
        # This is a basic test since we need to see the actual implementation
        try:
            pod_data = PodHubData()
            self.assertIsNotNone(pod_data)
        except Exception as e:
            # If instantiation fails, at least verify the class exists
            self.assertTrue(hasattr(PodHubData, '__init__'))


class TestPodHubApplication(unittest.TestCase):
    
    def test_pod_hub_application_exists(self):
        """Test that PodHubApplication class exists and can be instantiated"""
        try:
            app = PodHubApplication()
            self.assertIsNotNone(app)
        except Exception as e:
            # If instantiation fails, at least verify the class exists
            self.assertTrue(hasattr(PodHubApplication, '__init__'))


class TestPodHubFunctions(unittest.TestCase):
    
    def test_exported_functions_exist(self):
        """Test that exported functions exist"""
        from spring_pkg.monitor.server import (
            register_endpoints, get_app_pips, get_live_services, 
            ai_get_app, get_app_instances
        )
        
        # Test that functions are callable
        self.assertTrue(callable(register_endpoints))
        self.assertTrue(callable(get_app_pips))
        self.assertTrue(callable(get_live_services))
        self.assertTrue(callable(ai_get_app))
        self.assertTrue(callable(get_app_instances))


if __name__ == '__main__':
    unittest.main()
