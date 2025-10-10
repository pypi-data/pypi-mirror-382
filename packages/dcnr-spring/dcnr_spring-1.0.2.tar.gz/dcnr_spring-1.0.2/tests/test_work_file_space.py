import unittest
import tempfile
import os
import shutil
import json
import uuid
from unittest.mock import patch, MagicMock

from spring_pkg.utils.work_file_space import WorkingFileSpace


class TestWorkingFileSpace(unittest.TestCase):
    """Test cases for WorkingFileSpace class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_parent_dir = tempfile.mkdtemp()
        self.test_dirname = "test_workspace"
        self.test_userinfo = {"test": "data"}

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_parent_dir):
            shutil.rmtree(self.test_parent_dir, ignore_errors=True)

    def test_init_default_parameters(self):
        """Test WorkingFileSpace initialization with default parameters."""
        wfs = WorkingFileSpace()
        self.assertEqual(wfs.parent_dir, WorkingFileSpace.TMP_DIR_ROOT)
        self.assertIsNotNone(wfs.dirname)
        self.assertEqual(wfs.persistent, False)
        self.assertEqual(wfs.userinfo, {})

    def test_init_with_custom_parameters(self):
        """Test WorkingFileSpace initialization with custom parameters."""
        wfs = WorkingFileSpace(
            parent_dir=self.test_parent_dir,
            dirname=self.test_dirname,
            userinfo=self.test_userinfo,
            persistent=True
        )
        self.assertEqual(wfs.parent_dir, self.test_parent_dir)
        self.assertEqual(wfs.dirname, self.test_dirname)
        self.assertEqual(wfs.persistent, True)
        self.assertEqual(wfs.userinfo, self.test_userinfo)

    def test_init_with_existing_dir(self):
        """Test WorkingFileSpace initialization with existing directory."""
        existing_dir = os.path.join(self.test_parent_dir, "existing")
        os.makedirs(existing_dir)
        
        wfs = WorkingFileSpace(existing_dir=existing_dir)
        self.assertEqual(wfs.dirpath, existing_dir)
        self.assertEqual(wfs.persistent, True)
        self.assertEqual(wfs.parent_dir, self.test_parent_dir)
        self.assertEqual(wfs.dirname, "existing")

    def test_context_manager_creates_directory(self):
        """Test that context manager creates the working directory."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            self.assertTrue(os.path.exists(wfs.dirpath))
            self.assertTrue(os.path.isdir(wfs.dirpath))

    def test_context_manager_removes_directory_non_persistent(self):
        """Test that context manager removes directory when not persistent."""
        dirpath = None
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname, persistent=False) as wfs:
            dirpath = wfs.dirpath
            self.assertTrue(os.path.exists(dirpath))

        # Directory should be removed after exiting context
        self.assertFalse(os.path.exists(dirpath))

    def test_context_manager_keeps_directory_persistent(self):
        """Test that context manager keeps directory when persistent."""
        dirpath = None
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname, persistent=True) as wfs:
            dirpath = wfs.dirpath
            self.assertTrue(os.path.exists(dirpath))

        # Directory should still exist after exiting context
        self.assertTrue(os.path.exists(dirpath))

    def test_get_file_name_with_name(self):
        """Test get_file_name method with provided name."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            filename = wfs.get_file_name("test.txt")
            expected = os.path.join(wfs.dirpath, "test.txt")
            self.assertEqual(filename, expected)

    def test_get_file_name_without_name(self):
        """Test get_file_name method without provided name (generates UUID)."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            filename = wfs.get_file_name()
            # Should be a valid UUID
            basename = os.path.basename(filename)
            try:
                uuid.UUID(basename)
            except ValueError:
                self.fail("Generated filename is not a valid UUID")

    def test_mkdir(self):
        """Test mkdir method."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            subdir = wfs.mkdir("testdir")
            self.assertTrue(os.path.exists(subdir))
            self.assertTrue(os.path.isdir(subdir))
            expected = os.path.join(wfs.dirpath, "testdir")
            self.assertEqual(subdir, expected)

    def test_mkdir_nested(self):
        """Test mkdir method with nested directories."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            subdir = wfs.mkdir("level1/level2/level3")
            self.assertTrue(os.path.exists(subdir))
            self.assertTrue(os.path.isdir(subdir))

    def test_write_and_read_json(self):
        """Test write_json and read_json methods."""
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            wfs.write_json("test.json", test_data)
            
            # File should exist
            json_path = os.path.join(wfs.dirpath, "test.json")
            self.assertTrue(os.path.exists(json_path))
            
            # Read back the data
            read_data = wfs.read_json("test.json")
            self.assertEqual(read_data, test_data)

    def test_read_json_nonexistent_file(self):
        """Test read_json with non-existent file."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            result = wfs.read_json("nonexistent.json")
            self.assertIsNone(result)

    def test_write_and_read_text(self):
        """Test write_text and read_text methods."""
        test_text = "Hello, World!\nThis is a test file."
        
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            wfs.write_text("test.txt", test_text)
            
            # File should exist
            text_path = os.path.join(wfs.dirpath, "test.txt")
            self.assertTrue(os.path.exists(text_path))
            
            # Read back the text
            read_text = wfs.read_text("test.txt")
            self.assertEqual(read_text, test_text)

    def test_read_text_nonexistent_file(self):
        """Test read_text with non-existent file."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            result = wfs.read_text("nonexistent.txt")
            self.assertIsNone(result)

    def test_write_exception(self):
        """Test write_exception method."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            try:
                raise ValueError("Test exception")
            except ValueError:
                wfs.write_exception("exception.txt")
                
                # File should exist
                exc_path = os.path.join(wfs.dirpath, "exception.txt")
                self.assertTrue(os.path.exists(exc_path))

    def test_write_stacktrace(self):
        """Test write_stacktrace method."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname) as wfs:
            wfs.write_stacktrace("stacktrace.txt")
            
            # File should exist
            stack_path = os.path.join(wfs.dirpath, "stacktrace.txt")
            self.assertTrue(os.path.exists(stack_path))

    def test_remove_oldest_when_many_dirs(self):
        """Test that oldest directory is removed when there are many directories."""
        # Create 10 directories
        for i in range(10):
            test_dir = os.path.join(self.test_parent_dir, f"dir_{i}")
            os.makedirs(test_dir)
        
        # Create another directory using WorkingFileSpace
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname="new_dir") as wfs:
            # Should have removed one old directory
            remaining_dirs = os.listdir(self.test_parent_dir)
            # Should have 10 directories (9 old + 1 new)
            self.assertEqual(len(remaining_dirs), 10)

    @patch('spring_pkg.utils.work_file_space.send')
    def test_will_remove_dirs_calls_send(self, mock_send):
        """Test that will_remove_dirs calls the send function."""
        with WorkingFileSpace(parent_dir=self.test_parent_dir, dirname=self.test_dirname, userinfo=self.test_userinfo) as wfs:
            pass  # Exit context to trigger will_remove_dirs
        
        # Check that send was called
        mock_send.assert_called_once_with(
            'workingfilespace-will-remove-dirs',
            {'dirpath': wfs.dirpath, 'userinfo': self.test_userinfo}
        )


if __name__ == '__main__':
    unittest.main()
