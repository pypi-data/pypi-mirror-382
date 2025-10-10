import unittest
import threading
import time
from unittest.mock import patch, MagicMock

from spring_pkg.notifications.core import (
    send, register, unregister, 
    NotificationCenter, NotificationTarget, NotificationData,
    _ns_register_client, _ns_send_notification, _ns_unregister_client
)


class TestNotificationCenter(unittest.TestCase):
    """Test cases for notification center functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear notification center before each test
        NotificationCenter.notifications.clear()
        NotificationCenter.id = 1

    def tearDown(self):
        """Clean up after tests."""
        # Clear notification center after each test
        NotificationCenter.notifications.clear()
        NotificationCenter.id = 1

    def test_notification_target_dataclass(self):
        """Test NotificationTarget dataclass."""
        target_func = lambda x, y, z: None
        userdata = {"test": "data"}
        target = NotificationTarget(target=target_func, userdata=userdata, id=1)
        
        self.assertEqual(target.target, target_func)
        self.assertEqual(target.userdata, userdata)
        self.assertEqual(target.id, 1)

    def test_notification_data_dataclass(self):
        """Test NotificationData dataclass."""
        clients = []
        data = NotificationData(clients=clients)
        self.assertEqual(data.clients, clients)

    def test_register_new_notification(self):
        """Test registering for a new notification."""
        def test_handler(notif_name, data, userdata):
            pass
        
        client_id = register("test_notification", test_handler, {"user": "data"})
        
        # Should return a valid client ID
        self.assertIsInstance(client_id, int)
        self.assertEqual(client_id, 1)
        
        # Notification should be registered
        self.assertIn("test_notification", NotificationCenter.notifications)
        self.assertEqual(len(NotificationCenter.notifications["test_notification"].clients), 1)

    def test_register_existing_notification(self):
        """Test registering additional clients for existing notification."""
        def handler1(notif_name, data, userdata):
            pass
        
        def handler2(notif_name, data, userdata):
            pass
        
        client_id1 = register("test_notification", handler1)
        client_id2 = register("test_notification", handler2)
        
        # Should have different client IDs
        self.assertNotEqual(client_id1, client_id2)
        
        # Should have 2 clients for the same notification
        self.assertEqual(len(NotificationCenter.notifications["test_notification"].clients), 2)

    def test_send_notification_no_clients(self):
        """Test sending notification with no registered clients."""
        sent_count = send("nonexistent_notification", {"data": "test"})
        self.assertEqual(sent_count, 0)

    def test_send_notification_with_clients(self):
        """Test sending notification to registered clients."""
        received_notifications = []
        
        def handler1(notif_name, data, userdata):
            received_notifications.append(("handler1", notif_name, data, userdata))
        
        def handler2(notif_name, data, userdata):
            received_notifications.append(("handler2", notif_name, data, userdata))
        
        # Register handlers
        register("test_notification", handler1, "user1")
        register("test_notification", handler2, "user2")
        
        # Send notification
        test_data = {"message": "hello"}
        sent_count = send("test_notification", test_data)
        
        # Should have sent to 2 clients
        self.assertEqual(sent_count, 2)
        
        # Both handlers should have received the notification
        self.assertEqual(len(received_notifications), 2)
        
        # Check received data
        for handler_name, notif_name, data, userdata in received_notifications:
            self.assertEqual(notif_name, "test_notification")
            self.assertEqual(data, test_data)
            if handler_name == "handler1":
                self.assertEqual(userdata, "user1")
            else:
                self.assertEqual(userdata, "user2")

    def test_unregister_by_client_id(self):
        """Test unregistering a specific client."""
        def handler(notif_name, data, userdata):
            pass
        
        client_id = register("test_notification", handler)
        
        # Should have 1 client
        self.assertEqual(len(NotificationCenter.notifications["test_notification"].clients), 1)
        
        # Unregister the client
        unregister("test_notification", client_id)
        
        # Should have 0 clients
        self.assertEqual(len(NotificationCenter.notifications["test_notification"].clients), 0)

    def test_unregister_by_notification_name(self):
        """Test unregistering all clients for a notification."""
        def handler1(notif_name, data, userdata):
            pass
        
        def handler2(notif_name, data, userdata):
            pass
        
        register("test_notification", handler1)
        register("test_notification", handler2)
        
        # Should have the notification registered
        self.assertIn("test_notification", NotificationCenter.notifications)
        
        # Unregister entire notification
        unregister("test_notification")
        
        # Notification should be removed
        self.assertNotIn("test_notification", NotificationCenter.notifications)

    def test_unregister_nonexistent_client(self):
        """Test unregistering non-existent client."""
        def handler(notif_name, data, userdata):
            pass
        
        register("test_notification", handler)
        
        # Try to unregister non-existent client
        result = _ns_unregister_client("test_notification", 999)
        self.assertFalse(result)

    def test_unregister_nonexistent_notification(self):
        """Test unregistering from non-existent notification."""
        result = _ns_unregister_client("nonexistent", 1)
        self.assertFalse(result)

    def test_send_notification_with_exception_in_handler(self):
        """Test sending notification when handler raises exception."""
        received_count = 0
        
        def good_handler(notif_name, data, userdata):
            nonlocal received_count
            received_count += 1
        
        def bad_handler(notif_name, data, userdata):
            raise ValueError("Handler error")
        
        def another_good_handler(notif_name, data, userdata):
            nonlocal received_count
            received_count += 1
        
        # Register handlers (one that will fail)
        register("test_notification", good_handler)
        register("test_notification", bad_handler)
        register("test_notification", another_good_handler)
        
        # Send notification - should not raise exception
        with patch('spring_pkg.notifications.core.logger') as mock_logger:
            sent_count = send("test_notification", {"data": "test"})
            
            # Should report sending to all 3, even though one failed
            self.assertEqual(sent_count, 2)  # Only successful sends are counted
            
            # Logger should have been called for the exception
            mock_logger.exception.assert_called_once()
        
        # Good handlers should have received the notification
        self.assertEqual(received_count, 2)

    def test_thread_safety(self):
        """Test thread safety of notification system."""
        results = []
        
        def handler(notif_name, data, userdata):
            results.append(data)
        
        def register_worker():
            for i in range(10):
                register(f"notification_{i}", handler)
        
        def send_worker():
            for i in range(10):
                send(f"notification_{i}", f"data_{i}")
        
        # Create multiple threads for registration and sending
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=register_worker))
            threads.append(threading.Thread(target=send_worker))
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should not have crashed and should have some results
        # (exact number depends on timing, but should be reasonable)
        self.assertGreater(len(results), 0)

    def test_client_id_increments(self):
        """Test that client IDs increment properly."""
        def handler(notif_name, data, userdata):
            pass
        
        id1 = register("test1", handler)
        id2 = register("test2", handler)
        id3 = register("test1", handler)  # Same notification, different client
        
        # IDs should be sequential
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)
        self.assertEqual(id3, 3)

    def test_send_with_none_data(self):
        """Test sending notification with None data."""
        received_data = []
        
        def handler(notif_name, data, userdata):
            received_data.append(data)
        
        register("test_notification", handler)
        sent_count = send("test_notification", None)
        
        self.assertEqual(sent_count, 1)
        self.assertEqual(received_data[0], None)

    def test_send_without_data_parameter(self):
        """Test sending notification without data parameter."""
        received_data = []
        
        def handler(notif_name, data, userdata):
            received_data.append(data)
        
        register("test_notification", handler)
        sent_count = send("test_notification")  # No data parameter
        
        self.assertEqual(sent_count, 1)
        self.assertIsNone(received_data[0])


if __name__ == '__main__':
    unittest.main()
