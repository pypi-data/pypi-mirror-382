import unittest
import tempfile
import os
import pickle
from unittest.mock import patch

from spring_pkg.subprocess import (
    SubprocessArguments, SubprocessResult, SubprocessPickle, 
    SubprocessPickleRunner, SUBPROCESS_ENV_NAME, is_subprocess
)


class TestSubprocessArguments(unittest.TestCase):
    """Test cases for SubprocessArguments class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_args = [1, 2, 'hello', {'key': 'value'}]
        self.test_kwargs = {'param1': 'value1', 'param2': 42, 'param3': [1, 2, 3]}
        self.temp_file = None

    def tearDown(self):
        """Clean up after tests."""
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)

    def test_init(self):
        """Test SubprocessArguments initialization."""
        args_obj = SubprocessArguments(self.test_args, self.test_kwargs)
        self.assertEqual(args_obj.args, self.test_args)
        self.assertEqual(args_obj.kwargs, self.test_kwargs)

    def test_to_file_and_from_file(self):
        """Test serialization and deserialization."""
        args_obj = SubprocessArguments(self.test_args, self.test_kwargs)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.temp_file = tf.name
        
        # Serialize to file
        args_obj.to_file(self.temp_file)
        
        # File should exist
        self.assertTrue(os.path.exists(self.temp_file))
        
        # Deserialize from file
        loaded_args = SubprocessArguments.from_file(self.temp_file)
        
        # Data should be preserved
        self.assertEqual(loaded_args.args, self.test_args)
        self.assertEqual(loaded_args.kwargs, self.test_kwargs)

    def test_empty_args_kwargs(self):
        """Test with empty args and kwargs."""
        args_obj = SubprocessArguments([], {})
        
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.temp_file = tf.name
        
        args_obj.to_file(self.temp_file)
        loaded_args = SubprocessArguments.from_file(self.temp_file)
        
        self.assertEqual(loaded_args.args, [])
        self.assertEqual(loaded_args.kwargs, {})

    def test_complex_data_types(self):
        """Test with complex data types."""
        complex_args = [
            {'nested': {'dict': True}},
            [1, [2, [3, 4]]],
            set([1, 2, 3]),
            (1, 2, 3)
        ]
        complex_kwargs = {
            'complex_dict': {'a': {'b': {'c': 'd'}}},
            'tuple_list': [(1, 2), (3, 4)],
            'mixed': [{'key': 'value'}, [1, 2, 3], 'string']
        }
        
        args_obj = SubprocessArguments(complex_args, complex_kwargs)
        
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.temp_file = tf.name
        
        args_obj.to_file(self.temp_file)
        loaded_args = SubprocessArguments.from_file(self.temp_file)
        
        # Complex objects should be preserved
        self.assertEqual(loaded_args.args[0], complex_args[0])
        self.assertEqual(loaded_args.args[1], complex_args[1])
        self.assertEqual(loaded_args.kwargs['complex_dict'], complex_kwargs['complex_dict'])


class TestSubprocessResult(unittest.TestCase):
    """Test cases for SubprocessResult class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = None

    def tearDown(self):
        """Clean up after tests."""
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)

    def test_init_minimal(self):
        """Test SubprocessResult initialization with minimal parameters."""
        result = SubprocessResult('success')
        self.assertEqual(result.status, 'success')
        self.assertIsNone(result.result)
        self.assertIsNone(result.error)
        self.assertIsNone(result.type)
        self.assertIsNone(result.stack)
        self.assertIsNone(result.exception_obj)

    def test_init_full(self):
        """Test SubprocessResult initialization with all parameters."""
        test_result = {'output': 'test output'}
        test_error = 'test error message'
        test_type = 'ValueError'
        test_stack = 'stack trace here'
        test_exception_obj = b'pickled exception'
        
        result = SubprocessResult(
            status='error',
            result=test_result,
            error=test_error,
            type=test_type,
            stack=test_stack,
            exception_obj=test_exception_obj
        )
        
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.result, test_result)
        self.assertEqual(result.error, test_error)
        self.assertEqual(result.type, test_type)
        self.assertEqual(result.stack, test_stack)
        self.assertEqual(result.exception_obj, test_exception_obj)

    def test_to_file_and_from_file(self):
        """Test serialization and deserialization of SubprocessResult."""
        original_result = SubprocessResult(
            status='completed',
            result={'data': [1, 2, 3], 'message': 'success'},
            error=None,
            type=None,
            stack=None,
            exception_obj=None
        )
        
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.temp_file = tf.name
        
        # Serialize to file
        original_result.to_file(self.temp_file)
        
        # File should exist
        self.assertTrue(os.path.exists(self.temp_file))
        
        # Deserialize from file
        loaded_result = SubprocessResult.from_file(self.temp_file)
        
        # Data should be preserved
        self.assertEqual(loaded_result.status, original_result.status)
        self.assertEqual(loaded_result.result, original_result.result)
        self.assertEqual(loaded_result.error, original_result.error)
        self.assertEqual(loaded_result.type, original_result.type)
        self.assertEqual(loaded_result.stack, original_result.stack)
        self.assertEqual(loaded_result.exception_obj, original_result.exception_obj)

    def test_error_result(self):
        """Test SubprocessResult for error cases."""
        error_result = SubprocessResult(
            status='error',
            result=None,
            error='Division by zero',
            type='ZeroDivisionError',
            stack='Traceback (most recent call last):\n  File...',
            exception_obj=pickle.dumps(ZeroDivisionError('Division by zero'))
        )
        
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.temp_file = tf.name
        
        error_result.to_file(self.temp_file)
        loaded_result = SubprocessResult.from_file(self.temp_file)
        
        self.assertEqual(loaded_result.status, 'error')
        self.assertEqual(loaded_result.error, 'Division by zero')
        self.assertEqual(loaded_result.type, 'ZeroDivisionError')
        self.assertIsNotNone(loaded_result.exception_obj)


class TestSubprocessEnvFunctions(unittest.TestCase):
    """Test cases for subprocess environment functions."""

    def test_is_subprocess_false_default(self):
        """Test is_subprocess returns False by default."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(is_subprocess())

    def test_is_subprocess_false_with_zero(self):
        """Test is_subprocess returns False when env var is '0'."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: '0'}):
            self.assertFalse(is_subprocess())

    def test_is_subprocess_false_with_false(self):
        """Test is_subprocess returns False when env var is 'false'."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'false'}):
            self.assertFalse(is_subprocess())

    def test_is_subprocess_false_with_no(self):
        """Test is_subprocess returns False when env var is 'no'."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'no'}):
            self.assertFalse(is_subprocess())

    def test_is_subprocess_true_with_one(self):
        """Test is_subprocess returns True when env var is '1'."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: '1'}):
            self.assertTrue(is_subprocess())

    def test_is_subprocess_true_with_true(self):
        """Test is_subprocess returns True when env var is 'true'."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'true'}):
            self.assertTrue(is_subprocess())

    def test_is_subprocess_true_with_yes(self):
        """Test is_subprocess returns True when env var is 'yes'."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'yes'}):
            self.assertTrue(is_subprocess())

    def test_is_subprocess_case_insensitive(self):
        """Test is_subprocess is case insensitive."""
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'TRUE'}):
            self.assertTrue(is_subprocess())
        
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'False'}):
            self.assertFalse(is_subprocess())
        
        with patch.dict(os.environ, {SUBPROCESS_ENV_NAME: 'YES'}):
            self.assertTrue(is_subprocess())

    def test_subprocess_env_name_constant(self):
        """Test that SUBPROCESS_ENV_NAME constant is defined correctly."""
        self.assertEqual(SUBPROCESS_ENV_NAME, 'DCNR_SPRING_SUBPROCESS')


if __name__ == '__main__':
    unittest.main()
