import unittest
import pickle
from unittest.mock import patch, MagicMock

from spring_pkg.requests.message_request_client import MessageServiceClient
from spring_pkg.requests.empty_message_service import EmptyMessageService


class TestMessageServiceClient(unittest.TestCase):
    """Test cases for MessageServiceClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MessageServiceClient(
            uploader_user="test_user",
            correlation_id="test_correlation_123",
            job_id="job_456",
            user_data={"key": "value"}
        )

    def test_initialization(self):
        """Test MessageServiceClient initialization."""
        self.assertEqual(self.client.uploader_user, "test_user")
        self.assertEqual(self.client.correlation_id, "test_correlation_123")
        self.assertEqual(self.client.job_id, "job_456")
        self.assertEqual(self.client.user_data, {"key": "value"})

    def test_initialization_with_defaults(self):
        """Test MessageServiceClient initialization with default values."""
        client = MessageServiceClient()
        self.assertIsNone(client.uploader_user)
        self.assertIsNone(client.correlation_id)
        self.assertIsNone(client.job_id)
        self.assertIsNone(client.user_data)

    def test_logger_creation(self):
        """Test that logger is created with correct name."""
        self.assertIsNotNone(self.client.logger)
        expected_name = "MessageServiceClient-test_correlation_123"
        self.assertEqual(self.client.logger.name, expected_name)

    def test_logger_with_none_correlation_id(self):
        """Test logger creation when correlation_id is None."""
        client = MessageServiceClient()
        self.assertIsNotNone(client.logger)
        expected_name = "MessageServiceClient-None"
        self.assertEqual(client.logger.name, expected_name)

    def test_complete_job_base_implementation(self):
        """Test that complete_job base implementation does nothing."""
        # Should not raise any exceptions
        self.client.complete_job({"result": "success"})

    def test_fail_job_base_implementation(self):
        """Test that fail_job base implementation does nothing."""
        # Should not raise any exceptions
        self.client.fail_job("Test error")

    def test_send_back_base_implementation(self):
        """Test that send_back base implementation does nothing."""
        # Should not raise any exceptions
        self.client.send_back({"response": "data"})

    def test_send_error_base_implementation(self):
        """Test that send_error base implementation does nothing."""
        # Should not raise any exceptions
        self.client.send_error("Error message")

    def test_complete_message_base_implementation(self):
        """Test that complete_message base implementation does nothing."""
        # Should not raise any exceptions
        self.client.complete_message()

    def test_get_async_producer(self):
        """Test get_async_producer method."""
        producer = self.client.get_async_producer()
        
        # Should return pickled version of self
        self.assertIsInstance(producer, bytes)
        
        # Should be able to unpickle and get the same object
        unpickled = pickle.loads(producer)
        self.assertEqual(unpickled.uploader_user, self.client.uploader_user)
        self.assertEqual(unpickled.correlation_id, self.client.correlation_id)
        self.assertEqual(unpickled.job_id, self.client.job_id)
        self.assertEqual(unpickled.user_data, self.client.user_data)

    def test_serialization_roundtrip(self):
        """Test that client can be serialized and deserialized."""
        # Serialize
        serialized = pickle.dumps(self.client)
        
        # Deserialize
        deserialized = pickle.loads(serialized)
        
        # Check that all attributes are preserved
        self.assertEqual(deserialized.uploader_user, self.client.uploader_user)
        self.assertEqual(deserialized.correlation_id, self.client.correlation_id)
        self.assertEqual(deserialized.job_id, self.client.job_id)
        self.assertEqual(deserialized.user_data, self.client.user_data)


class TestEmptyMessageService(unittest.TestCase):
    """Test cases for EmptyMessageService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = EmptyMessageService(
            uploader_user="test_user",
            correlation_id="test_correlation",
            job_id="test_job"
        )

    def test_inheritance(self):
        """Test that EmptyMessageService inherits from MessageServiceClient."""
        self.assertIsInstance(self.service, MessageServiceClient)

    def test_initialization(self):
        """Test EmptyMessageService initialization."""
        self.assertEqual(self.service.uploader_user, "test_user")
        self.assertEqual(self.service.correlation_id, "test_correlation")
        self.assertEqual(self.service.job_id, "test_job")
        
        # New attributes should be initialized
        self.assertIsNone(self.service.send_back_value)
        self.assertIsNone(self.service.send_error_value)
        self.assertFalse(self.service.message_completed)

    def test_complete_job(self):
        """Test complete_job functionality."""
        test_data = {"result": "success", "items": [1, 2, 3]}
        
        self.service.complete_job(test_data)
        
        self.assertEqual(self.service.send_back_value, test_data)
        self.assertTrue(self.service.message_completed)

    def test_fail_job(self):
        """Test fail_job functionality."""
        test_error = "Something went wrong"
        
        self.service.fail_job(test_error)
        
        self.assertEqual(self.service.send_error_value, test_error)
        self.assertTrue(self.service.message_completed)

    def test_send_back(self):
        """Test send_back method."""
        test_data = {"response": "ok"}
        
        self.service.send_back(test_data)
        
        # send_back should call complete_job
        self.assertEqual(self.service.send_back_value, test_data)
        self.assertTrue(self.service.message_completed)

    def test_send_error(self):
        """Test send_error method."""
        test_error = "Test error message"
        
        self.service.send_error(test_error)
        
        # send_error should call fail_job
        self.assertEqual(self.service.send_error_value, test_error)
        self.assertTrue(self.service.message_completed)

    def test_complete_message(self):
        """Test complete_message method."""
        self.assertFalse(self.service.message_completed)
        
        self.service.complete_message()
        
        self.assertTrue(self.service.message_completed)

    def test_multiple_operations(self):
        """Test multiple operations on the same service."""
        # First complete with data
        self.service.complete_job({"data": "first"})
        self.assertEqual(self.service.send_back_value, {"data": "first"})
        self.assertTrue(self.service.message_completed)
        
        # Reset completed flag for next operation
        self.service.message_completed = False
        
        # Then fail with error
        self.service.fail_job("error occurred")
        self.assertEqual(self.service.send_error_value, "error occurred")
        self.assertTrue(self.service.message_completed)

    def test_state_tracking(self):
        """Test that service tracks state correctly."""
        # Initially no values set
        self.assertIsNone(self.service.send_back_value)
        self.assertIsNone(self.service.send_error_value)
        self.assertFalse(self.service.message_completed)
        
        # After send_back
        self.service.send_back("success")
        self.assertEqual(self.service.send_back_value, "success")
        self.assertIsNone(self.service.send_error_value)
        self.assertTrue(self.service.message_completed)
        
        # Reset and try send_error
        self.service.send_back_value = None
        self.service.message_completed = False
        
        self.service.send_error("failure")
        self.assertIsNone(self.service.send_back_value)
        self.assertEqual(self.service.send_error_value, "failure")
        self.assertTrue(self.service.message_completed)

    def test_complex_data_handling(self):
        """Test handling of complex data types."""
        complex_data = {
            "nested": {"dict": True},
            "list": [1, 2, {"inner": "value"}],
            "tuple": (1, 2, 3),
            "string": "test",
            "number": 42.5
        }
        
        self.service.complete_job(complex_data)
        
        self.assertEqual(self.service.send_back_value, complex_data)
        self.assertTrue(self.service.message_completed)

    def test_error_types(self):
        """Test different types of error values."""
        # String error
        self.service.fail_job("String error")
        self.assertEqual(self.service.send_error_value, "String error")
        
        # Reset
        self.service.send_error_value = None
        self.service.message_completed = False
        
        # Dictionary error
        error_dict = {"error_code": 500, "message": "Internal error"}
        self.service.fail_job(error_dict)
        self.assertEqual(self.service.send_error_value, error_dict)
        
        # Reset
        self.service.send_error_value = None
        self.service.message_completed = False
        
        # Exception as error
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.service.fail_job(e)
            self.assertEqual(self.service.send_error_value, e)

    def test_inheritance_properties(self):
        """Test that inherited properties work correctly."""
        # Should have inherited logger
        self.assertIsNotNone(self.service.logger)
        
        # Should have get_async_producer method
        producer = self.service.get_async_producer()
        self.assertIsInstance(producer, bytes)
        
        # Should be able to deserialize
        deserialized = pickle.loads(producer)
        self.assertIsInstance(deserialized, EmptyMessageService)
        self.assertEqual(deserialized.uploader_user, self.service.uploader_user)


if __name__ == '__main__':
    unittest.main()
