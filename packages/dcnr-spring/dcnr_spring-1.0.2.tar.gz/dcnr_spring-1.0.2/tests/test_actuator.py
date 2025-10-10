import unittest
from unittest.mock import MagicMock

from spring_pkg.actuator.root import (
    STATUS_OK, STATUS_FAIL, STATUS_UNKNOWN,
    is_ok, register_actuator_component, on_actuator_root,
    get_actuator_components, get_component_response, on_actuator_endpoint,
    _glob_pages
)


class TestActuatorRoot(unittest.TestCase):
    """Test cases for actuator root functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear global pages before each test
        _glob_pages.clear()

    def tearDown(self):
        """Clean up after tests."""
        # Clear global pages after each test
        _glob_pages.clear()

    def test_status_constants(self):
        """Test that status constants are defined correctly."""
        self.assertEqual(STATUS_OK, 'UP')
        self.assertEqual(STATUS_FAIL, 'DOWN')
        self.assertEqual(STATUS_UNKNOWN, 'NA')

    def test_register_actuator_component(self):
        """Test registering actuator components."""
        def test_callback():
            return {'status': STATUS_OK}
        
        register_actuator_component('test_component', test_callback)
        
        # Component should be registered
        self.assertIn('test_component', _glob_pages)
        self.assertEqual(_glob_pages['test_component'], test_callback)

    def test_register_multiple_components(self):
        """Test registering multiple actuator components."""
        def callback1():
            return {'status': STATUS_OK}
        
        def callback2():
            return {'status': STATUS_FAIL}
        
        register_actuator_component('component1', callback1)
        register_actuator_component('component2', callback2)
        
        self.assertEqual(len(_glob_pages), 2)
        self.assertIn('component1', _glob_pages)
        self.assertIn('component2', _glob_pages)

    def test_is_ok_with_registered_component(self):
        """Test is_ok with registered component returning OK status."""
        def ok_callback():
            return {'status': STATUS_OK}
        
        register_actuator_component('test_component', ok_callback)
        self.assertTrue(is_ok('test_component'))

    def test_is_ok_with_failed_component(self):
        """Test is_ok with registered component returning FAIL status."""
        def fail_callback():
            return {'status': STATUS_FAIL}
        
        register_actuator_component('test_component', fail_callback)
        self.assertFalse(is_ok('test_component'))

    def test_is_ok_with_unknown_status(self):
        """Test is_ok with registered component returning unknown status."""
        def unknown_callback():
            return {'status': STATUS_UNKNOWN}
        
        register_actuator_component('test_component', unknown_callback)
        self.assertFalse(is_ok('test_component'))

    def test_is_ok_with_missing_status(self):
        """Test is_ok with registered component not returning status field."""
        def no_status_callback():
            return {'other_field': 'value'}
        
        register_actuator_component('test_component', no_status_callback)
        self.assertFalse(is_ok('test_component'))

    def test_is_ok_with_unregistered_component(self):
        """Test is_ok with unregistered component returns True."""
        self.assertTrue(is_ok('nonexistent_component'))

    def test_get_actuator_components_empty(self):
        """Test get_actuator_components with no registered components."""
        components = list(get_actuator_components())
        self.assertEqual(components, [])

    def test_get_actuator_components_with_components(self):
        """Test get_actuator_components with registered components."""
        def callback1():
            return {'status': STATUS_OK}
        
        def callback2():
            return {'status': STATUS_OK}
        
        register_actuator_component('comp1', callback1)
        register_actuator_component('comp2', callback2)
        
        components = list(get_actuator_components())
        self.assertIn('comp1', components)
        self.assertIn('comp2', components)
        self.assertEqual(len(components), 2)

    def test_get_component_response_existing(self):
        """Test get_component_response for existing component."""
        expected_response = {
            'status': STATUS_OK,
            'details': {
                'total': 1234567890,
                'free': 987654321
            }
        }
        
        def test_callback():
            return expected_response
        
        register_actuator_component('test_component', test_callback)
        response = get_component_response('test_component')
        
        self.assertEqual(response, expected_response)

    def test_get_component_response_nonexistent(self):
        """Test get_component_response for non-existent component."""
        response = get_component_response('nonexistent')
        expected = {'status': 'NA'}
        self.assertEqual(response, expected)

    def test_get_component_response_callback_returns_none(self):
        """Test get_component_response when callback returns None."""
        def none_callback():
            return None
        
        register_actuator_component('test_component', none_callback)
        response = get_component_response('test_component')
        
        expected = {'status': 'NA'}
        self.assertEqual(response, expected)

    def test_on_actuator_endpoint_root(self):
        """Test on_actuator_endpoint for root path."""
        def callback1():
            return {'status': STATUS_OK, 'detail': 'service1'}
        
        def callback2():
            return {'status': STATUS_FAIL, 'detail': 'service2'}
        
        register_actuator_component('service1', callback1)
        register_actuator_component('service2', callback2)
        
        response = on_actuator_endpoint('')
        
        self.assertEqual(response['status'], 'UP')
        self.assertEqual(response['groups'], ['liveness', 'readiness'])
        self.assertIn('components', response)
        self.assertIn('service1', response['components'])
        self.assertIn('service2', response['components'])

    def test_on_actuator_endpoint_none_path(self):
        """Test on_actuator_endpoint with None path."""
        def callback():
            return {'status': STATUS_OK}
        
        register_actuator_component('test_service', callback)
        
        response = on_actuator_endpoint(None)
        
        self.assertEqual(response['status'], 'UP')
        self.assertIn('components', response)

    def test_on_actuator_endpoint_specific_component(self):
        """Test on_actuator_endpoint for specific component."""
        expected_response = {'status': STATUS_OK, 'memory': '512MB'}
        
        def test_callback():
            return expected_response
        
        register_actuator_component('memory', test_callback)
        
        response = on_actuator_endpoint('memory')
        self.assertEqual(response, expected_response)

    def test_on_actuator_endpoint_nonexistent_component(self):
        """Test on_actuator_endpoint for non-existent component."""
        response = on_actuator_endpoint('nonexistent')
        self.assertEqual(response, {})

    def test_on_actuator_root(self):
        """Test on_actuator_root function."""
        def callback():
            return {'status': STATUS_OK}
        
        register_actuator_component('test', callback)
        
        # on_actuator_root should be equivalent to on_actuator_endpoint('')
        root_response = on_actuator_root()
        endpoint_response = on_actuator_endpoint('')
        
        self.assertEqual(root_response, endpoint_response)

    def test_component_callback_with_exception(self):
        """Test behavior when component callback raises exception."""
        def failing_callback():
            raise ValueError("Callback error")
        
        register_actuator_component('failing_component', failing_callback)
        
        # This should raise an exception when called
        with self.assertRaises(ValueError):
            is_ok('failing_component')

    def test_component_response_structure(self):
        """Test that component responses have correct structure."""
        def detailed_callback():
            return {
                'status': STATUS_OK,
                'details': {
                    'total_memory': 8192,
                    'free_memory': 4096,
                    'used_memory': 4096,
                    'path': '/opt/app',
                    'exists': True
                }
            }
        
        register_actuator_component('memory', detailed_callback)
        
        response = get_component_response('memory')
        
        self.assertEqual(response['status'], STATUS_OK)
        self.assertIn('details', response)
        self.assertEqual(response['details']['total_memory'], 8192)
        self.assertEqual(response['details']['path'], '/opt/app')

    def test_overwrite_component(self):
        """Test overwriting an existing component."""
        def callback1():
            return {'status': STATUS_OK, 'version': '1.0'}
        
        def callback2():
            return {'status': STATUS_FAIL, 'version': '2.0'}
        
        register_actuator_component('service', callback1)
        self.assertEqual(get_component_response('service')['version'], '1.0')
        
        # Overwrite with new callback
        register_actuator_component('service', callback2)
        self.assertEqual(get_component_response('service')['version'], '2.0')
        self.assertEqual(get_component_response('service')['status'], STATUS_FAIL)


if __name__ == '__main__':
    unittest.main()
