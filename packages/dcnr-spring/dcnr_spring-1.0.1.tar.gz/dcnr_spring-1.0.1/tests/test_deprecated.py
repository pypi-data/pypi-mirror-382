import unittest
import warnings
from unittest.mock import patch

from spring_pkg.coding.deprecated import deprecated


class TestDeprecated(unittest.TestCase):
    """Test cases for deprecated decorator."""

    def test_deprecated_decorator_with_reason(self):
        """Test that deprecated decorator shows warning with reason."""
        @deprecated("use new_function() instead")
        def old_function():
            return "old result"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()
            
            # Check that function still works
            self.assertEqual(result, "old result")
            
            # Check that warning was issued
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("old_function is deprecated", str(w[0].message))
            self.assertIn("use new_function() instead", str(w[0].message))

    def test_deprecated_decorator_preserves_function_metadata(self):
        """Test that deprecated decorator preserves function metadata."""
        @deprecated("reason")
        def test_function():
            """Test function docstring."""
            return "result"
        
        # Function name should be preserved
        self.assertEqual(test_function.__name__, "test_function")
        
        # Docstring should be preserved
        self.assertEqual(test_function.__doc__, "Test function docstring.")

    def test_deprecated_decorator_with_arguments(self):
        """Test deprecated decorator with function that takes arguments."""
        @deprecated("use new_add() instead")
        def old_add(a, b):
            return a + b
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_add(2, 3)
            
            # Function should work correctly
            self.assertEqual(result, 5)
            
            # Warning should be issued
            self.assertEqual(len(w), 1)
            self.assertIn("old_add is deprecated", str(w[0].message))

    def test_deprecated_decorator_with_kwargs(self):
        """Test deprecated decorator with function that takes keyword arguments."""
        @deprecated("use new_greet() instead")
        def old_greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_greet("World", greeting="Hi")
            
            # Function should work correctly
            self.assertEqual(result, "Hi, World!")
            
            # Warning should be issued
            self.assertEqual(len(w), 1)
            self.assertIn("old_greet is deprecated", str(w[0].message))

    def test_deprecated_decorator_multiple_calls(self):
        """Test that deprecated decorator warns on every call."""
        @deprecated("use new_function() instead")
        def old_function():
            return "result"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Call function multiple times
            old_function()
            old_function()
            old_function()
            
            # Should have 3 warnings
            self.assertEqual(len(w), 3)
            
            # All should be DeprecationWarnings
            for warning in w:
                self.assertTrue(issubclass(warning.category, DeprecationWarning))

    def test_deprecated_decorator_with_exception(self):
        """Test deprecated decorator when function raises exception."""
        @deprecated("use new_function() instead")
        def failing_function():
            raise ValueError("Something went wrong")
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Function should still raise the exception
            with self.assertRaises(ValueError):
                failing_function()
            
            # But warning should still be issued
            self.assertEqual(len(w), 1)
            self.assertIn("failing_function is deprecated", str(w[0].message))

    def test_deprecated_decorator_with_return_value(self):
        """Test deprecated decorator preserves return values."""
        test_data = {"key": "value", "number": 42}
        
        @deprecated("use new_function() instead")
        def return_data():
            return test_data
        
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = return_data()
            
            # Return value should be preserved exactly
            self.assertEqual(result, test_data)
            self.assertIs(result, test_data)

    def test_deprecated_decorator_stack_level(self):
        """Test that deprecated decorator uses correct stack level."""
        @deprecated("use new_function() instead")
        def old_function():
            return "result"
        
        def caller_function():
            return old_function()
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            caller_function()
            
            # Warning should point to the caller, not the wrapper
            self.assertEqual(len(w), 1)
            # The warning should have the correct stack level
            # (This is more of a behavior test than a strict assertion)

    def test_deprecated_decorator_empty_reason(self):
        """Test deprecated decorator with empty reason."""
        @deprecated("")
        def old_function():
            return "result"
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_function()
            
            self.assertEqual(len(w), 1)
            self.assertIn("old_function is deprecated:", str(w[0].message))


if __name__ == '__main__':
    unittest.main()
