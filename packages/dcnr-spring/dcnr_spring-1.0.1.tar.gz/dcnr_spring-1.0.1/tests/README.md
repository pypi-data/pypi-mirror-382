# Tests for dcnr-spring Package

This directory contains comprehensive test suites for all exported functions and classes in the `dcnr-spring` package.

## Test Structure

The test suite covers all major components of the package:

### Core Test Files

- **`test_work_file_space.py`** - Tests for the `WorkingFileSpace` context manager
- **`test_safe_counter.py`** - Tests for the thread-safe `SafeCounter` class
- **`test_waitloop.py`** - Tests for the waitloop functionality
- **`test_deprecated.py`** - Tests for the `@deprecated` decorator
- **`test_notifications.py`** - Tests for the notification center system
- **`test_shutdown_testmode.py`** - Tests for shutdown service and test mode functionality
- **`test_actuator.py`** - Tests for the actuator endpoint system
- **`test_subprocess.py`** - Tests for subprocess utilities and classes
- **`test_requests.py`** - Tests for request handling utilities
- **`test_message_services.py`** - Tests for message service client classes
- **`test_monitor.py`** - Tests for memory watching and thread database functionality
- **`test_security.py`** - Tests for encryption/decryption functions
- **`test_package_structure.py`** - Tests for overall package structure and imports

### Utility Files

- **`run_tests.py`** - Test runner script to execute all tests
- **`__init__.py`** - Package initialization for tests

## Running Tests

### Run All Tests

To run the complete test suite:

```bash
cd tests
python run_tests.py
```

Or using Python's unittest module:

```bash
python -m unittest discover tests
```

### Run Specific Test Module

To run tests for a specific module:

```bash
cd tests
python run_tests.py test_work_file_space
```

Or directly:

```bash
python -m unittest tests.test_work_file_space
```

### Run Individual Test Class

```bash
python -m unittest tests.test_work_file_space.TestWorkingFileSpace
```

### Run Individual Test Method

```bash
python -m unittest tests.test_work_file_space.TestWorkingFileSpace.test_context_manager_creates_directory
```

## Test Coverage

The test suite provides comprehensive coverage of:

### Utils Module
- ✅ `WorkingFileSpace` - Context manager for temporary directories
- ✅ `SafeCounter` - Thread-safe counter implementation
- ✅ `waitloop_start` / `waitloop_is_at_exit` - Application lifecycle management

### Notifications Module
- ✅ `send` / `register` / `unregister` - Notification center functionality
- ✅ `shutdown_service` / `is_shutting_down` - Service shutdown management
- ✅ `set_test_mode` / `get_test_mode` - Test mode utilities
- ✅ `LockedValue` - Thread-safe status tracking

### Requests Module
- ✅ `StreamLogger` - Logging to string stream
- ✅ `MessageServiceClient` - Base message service class
- ✅ `EmptyMessageService` - Empty implementation for testing
- ✅ `message_counter` decorator - Request counting functionality

### Security Module
- ✅ `cipher` / `decipher` - XOR-based encryption functions

### Actuator Module
- ✅ Actuator endpoint registration and management
- ✅ Health check functionality
- ✅ Component status tracking

### Subprocess Module
- ✅ `SubprocessArguments` - Argument serialization
- ✅ `SubprocessResult` - Result handling
- ✅ `is_subprocess` - Environment detection
- ✅ Pickle-based subprocess communication classes

### Monitor Module
- ✅ Memory usage monitoring and alerting
- ✅ Thread database for correlation tracking
- ✅ Memory threshold management

### Coding Module
- ✅ `@deprecated` decorator - Deprecation warnings

## Test Features

### Thread Safety Testing
Many tests include concurrent execution scenarios to verify thread safety of:
- `SafeCounter`
- `LockedValue`
- Notification system
- Thread database
- Memory monitoring

### Error Handling
Tests verify proper error handling for:
- Invalid inputs
- Edge cases
- Exception propagation
- Resource cleanup

### Integration Testing
- Package import testing
- Cross-module functionality
- Usage pattern validation

### Mock and Patch Testing
Tests use mocking where appropriate for:
- File system operations
- External dependencies
- Time-dependent functionality
- System calls

## Requirements

The tests require:
- Python 3.6+
- Standard library `unittest` module
- The `dcnr-spring` package to be importable

No external testing dependencies are required - all tests use only the Python standard library.

## Test Output

The test runner provides detailed output including:
- Test results with pass/fail status
- Detailed error messages and tracebacks
- Test execution summary
- Coverage information

Example output:
```
Running dcnr-spring package tests...
======================================================================
test_initial_count (tests.test_safe_counter.TestSafeCounter) ... ok
test_increment (tests.test_safe_counter.TestSafeCounter) ... ok
...
======================================================================
TEST SUMMARY
======================================================================
Tests run: 150
Failures: 0
Errors: 0
Skipped: 0

✅ All tests passed!
```

## Contributing

When adding new functionality to the package:

1. Create corresponding test files in this directory
2. Follow the existing naming convention: `test_<module_name>.py`
3. Include comprehensive test coverage for all public APIs
4. Test both success and failure scenarios
5. Include thread safety tests where applicable
6. Update this README if adding new test categories

## Bug Fix Verification

The test suite includes a fix for a bug found in `spring_pkg.notifications.testmode.get_test_mode()` which was missing a return statement. This has been corrected and is now properly tested.
