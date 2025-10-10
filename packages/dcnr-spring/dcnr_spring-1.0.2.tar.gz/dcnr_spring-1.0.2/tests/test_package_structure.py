import unittest
import importlib
import sys
import os

# Add project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestPackageStructure(unittest.TestCase):
    """Test cases for overall package structure and imports."""

    def test_main_package_import(self):
        """Test that main package can be imported."""
        try:
            import spring_pkg
            self.assertTrue(hasattr(spring_pkg, '__all__'))
        except ImportError as e:
            self.fail(f"Failed to import spring_pkg: {e}")

    def test_all_submodules_import(self):
        """Test that all declared submodules can be imported."""
        import spring_pkg
        
        for module_name in spring_pkg.__all__:
            with self.subTest(module=module_name):
                try:
                    module = getattr(spring_pkg, module_name)
                    self.assertIsNotNone(module)
                except AttributeError as e:
                    self.fail(f"Module {module_name} not accessible: {e}")

    def test_utils_module_exports(self):
        """Test utils module exports."""
        from spring_pkg.utils import SafeCounter, waitloop_start, waitloop_is_at_exit
        
        # Test that classes and functions are callable
        self.assertTrue(callable(SafeCounter))
        self.assertTrue(callable(waitloop_start))
        self.assertTrue(callable(waitloop_is_at_exit))

    def test_notifications_module_exports(self):
        """Test notifications module exports."""
        from spring_pkg.notifications import (
            send, register, unregister, 
            shutdown_service, is_shutting_down,
            set_test_mode, get_test_mode
        )
        
        # Test that all functions are callable
        self.assertTrue(callable(send))
        self.assertTrue(callable(register))
        self.assertTrue(callable(unregister))
        self.assertTrue(callable(shutdown_service))
        self.assertTrue(callable(is_shutting_down))
        self.assertTrue(callable(set_test_mode))
        self.assertTrue(callable(get_test_mode))

    def test_requests_module_exports(self):
        """Test requests module exports."""
        from spring_pkg.requests import (
            StreamLogger, EmptyMessageService, MessageServiceClient, counter
        )
        
        # Test classes
        self.assertTrue(callable(StreamLogger))
        self.assertTrue(callable(EmptyMessageService))
        self.assertTrue(callable(MessageServiceClient))
        
        # Test counter module
        self.assertTrue(hasattr(counter, 'message_counter'))
        self.assertTrue(hasattr(counter, 'get_count'))
        self.assertTrue(hasattr(counter, 'wait_for_empty'))

    def test_security_module_exports(self):
        """Test security module exports."""
        from spring_pkg.security import ciphering
        
        self.assertTrue(hasattr(ciphering, 'cipher'))
        self.assertTrue(hasattr(ciphering, 'decipher'))
        self.assertTrue(callable(ciphering.cipher))
        self.assertTrue(callable(ciphering.decipher))

    def test_actuator_module_exports(self):
        """Test actuator module exports."""
        from spring_pkg.actuator import (
            on_actuator_endpoint, is_ok, register_actuator_component,
            on_actuator_root, get_actuator_components, get_component_response,
            STATUS_OK, STATUS_FAIL, STATUS_UNKNOWN
        )
        
        # Test functions
        self.assertTrue(callable(on_actuator_endpoint))
        self.assertTrue(callable(is_ok))
        self.assertTrue(callable(register_actuator_component))
        self.assertTrue(callable(on_actuator_root))
        self.assertTrue(callable(get_actuator_components))
        self.assertTrue(callable(get_component_response))
        
        # Test constants
        self.assertEqual(STATUS_OK, 'UP')
        self.assertEqual(STATUS_FAIL, 'DOWN')
        self.assertEqual(STATUS_UNKNOWN, 'NA')

    def test_coding_module_exports(self):
        """Test coding module exports."""
        from spring_pkg.coding import deprecated
        
        self.assertTrue(callable(deprecated))

    def test_subprocess_module_exports(self):
        """Test subprocess module exports."""
        from spring_pkg.subprocess import (
            SubprocessArguments, SubprocessPickleRunner, SubprocessPickle,
            SubprocessResult, SUBPROCESS_ENV_NAME, is_subprocess
        )
        
        # Test classes
        self.assertTrue(callable(SubprocessArguments))
        self.assertTrue(callable(SubprocessPickleRunner))
        self.assertTrue(callable(SubprocessPickle))
        self.assertTrue(callable(SubprocessResult))
        
        # Test constants and functions
        self.assertEqual(SUBPROCESS_ENV_NAME, 'DCNR_SPRING_SUBPROCESS')
        self.assertTrue(callable(is_subprocess))

    def test_monitor_module_exports(self):
        """Test monitor module exports."""
        from spring_pkg.monitor import (
            start_memory_watch, stop_memory_watch, add_threshold, 
            get_memory_usage, hist_memory_max, MemoryUsage,
            get_thread_record, get_live_threads, save_thread_data, get_thread_data
        )
        
        # Test memory watch functions
        self.assertTrue(callable(start_memory_watch))
        self.assertTrue(callable(stop_memory_watch))
        self.assertTrue(callable(add_threshold))
        self.assertTrue(callable(get_memory_usage))
        self.assertTrue(callable(hist_memory_max))
        self.assertTrue(callable(MemoryUsage))
        
        # Test thread db functions
        self.assertTrue(callable(get_thread_record))
        self.assertTrue(callable(get_live_threads))
        self.assertTrue(callable(save_thread_data))
        self.assertTrue(callable(get_thread_data))

    def test_module_all_attributes(self):
        """Test that modules have proper __all__ attributes where expected."""
        modules_with_all = [
            'spring_pkg',
            'spring_pkg.utils',
            'spring_pkg.notifications',
            'spring_pkg.requests',
            'spring_pkg.security.ciphering',
            'spring_pkg.actuator',
            'spring_pkg.coding',
            'spring_pkg.subprocess',
        ]
        
        for module_name in modules_with_all:
            with self.subTest(module=module_name):
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, '__all__'):
                        all_attr = getattr(module, '__all__')
                        self.assertIsInstance(all_attr, (list, tuple))
                        self.assertGreater(len(all_attr), 0)
                except ImportError:
                    # Some modules might not be importable in test environment
                    pass

    def test_no_import_errors(self):
        """Test that importing the package doesn't cause errors."""
        try:
            import spring_pkg
            import spring_pkg.utils
            import spring_pkg.notifications
            import spring_pkg.requests
            import spring_pkg.security
            import spring_pkg.actuator
            import spring_pkg.coding
            import spring_pkg.subprocess
            import spring_pkg.monitor
        except Exception as e:
            self.fail(f"Import error: {e}")

    def test_work_file_space_importable(self):
        """Test that WorkingFileSpace can be imported and used."""
        from spring_pkg.utils.work_file_space import WorkingFileSpace
        
        # Should be able to create instance
        wfs = WorkingFileSpace(dirname="test_import")
        self.assertIsNotNone(wfs)
        self.assertEqual(wfs.dirname, "test_import")

    def test_package_version_info(self):
        """Test package version and metadata if available."""
        import spring_pkg
        
        # Check if package has version info
        if hasattr(spring_pkg, '__version__'):
            self.assertIsInstance(spring_pkg.__version__, str)
        
        # Check if package has author info
        if hasattr(spring_pkg, '__author__'):
            self.assertIsInstance(spring_pkg.__author__, str)

    def test_circular_imports(self):
        """Test that there are no circular import issues."""
        # Try importing all main modules in different orders
        import spring_pkg.utils
        import spring_pkg.notifications
        import spring_pkg.requests
        import spring_pkg.security
        import spring_pkg.actuator
        import spring_pkg.coding
        import spring_pkg.subprocess
        import spring_pkg.monitor
        
        # Try importing in reverse order
        import spring_pkg.monitor
        import spring_pkg.subprocess
        import spring_pkg.coding
        import spring_pkg.actuator
        import spring_pkg.security
        import spring_pkg.requests
        import spring_pkg.notifications
        import spring_pkg.utils
        
        # Should not raise any errors


class TestPackageUsage(unittest.TestCase):
    """Test basic usage patterns of the package."""

    def test_basic_usage_pattern(self):
        """Test basic usage pattern from documentation."""
        from spring_pkg.utils import WorkingFileSpace
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with WorkingFileSpace(parent_dir=temp_dir, dirname="test") as ws:
                # Should be able to use basic functionality
                file_path = ws.get_file_name('test.txt')
                self.assertTrue(file_path.endswith('test.txt'))
                
                # Should be able to create subdirectories
                subdir = ws.mkdir('subdir')
                self.assertTrue(os.path.exists(subdir))

    def test_notification_system_usage(self):
        """Test basic notification system usage."""
        from spring_pkg.notifications import register, send, unregister
        
        received_notifications = []
        
        def test_handler(notif_name, data, userdata):
            received_notifications.append((notif_name, data, userdata))
        
        # Register handler
        client_id = register("test_notification", test_handler, "test_user")
        
        # Send notification
        sent_count = send("test_notification", {"message": "hello"})
        
        self.assertEqual(sent_count, 1)
        self.assertEqual(len(received_notifications), 1)
        
        # Clean up
        unregister("test_notification", client_id)

    def test_counter_decorator_usage(self):
        """Test message counter decorator usage."""
        from spring_pkg.requests.counter import message_counter, get_count
        
        @message_counter
        def test_function():
            return get_count()
        
        # Should return 1 during execution
        count_during_execution = test_function()
        self.assertEqual(count_during_execution, 1)
        
        # Should return 0 after execution
        self.assertEqual(get_count(), 0)

    def test_security_usage(self):
        """Test basic security functionality usage."""
        from spring_pkg.security.ciphering import cipher, decipher
        
        original = "Test message"
        key = "secret_key"
        
        encrypted = cipher(original, key)
        decrypted = decipher(encrypted, key)
        
        self.assertEqual(original, decrypted)
        self.assertNotEqual(original, encrypted)


if __name__ == '__main__':
    unittest.main()
