"""The work_file_space module implements class WorkingFileSpace used
for simplified handling of temporary files and folders.

# Usage


```python
import os
from dcnr_spring.utils import WorkingFileSpace

# optionaly set tmp dir, where temporary directories are created
# WorkingFileSpace.TMP_DIR_ROOT = '/opt/processing'

using WorkingFileSpace() as ws:
    # do processing here

    # get new file path (for newly created file)
    # only name is created, no file in the file system
    new_file_path = ws.get_file_name('file.txt')

    # get new file path, unique name
    new_file_2 = ws.get_file_name()

    # get new subdirectory
    # it is actually created by this function
    new_subdir_path = ws.mkdir('temp')

    # another subdirectory created
    # it can contain whole sub-path
    new_subdir_2 = ws.mkdir('temp/proc1/subs')
 
```

- **WorkingFileSpace** object will create new subdirectory named by new UUID, so this particular instance will use directory for example like /opt/processing/b4b52995-b0d6-4b0e-8079-82aea434cc11
- **get_file_name** function creates new name for file, but file itself should be created by user code
- **mkdir** function creates subdirectory in the file system, so returned path can be used by user code
- during exit from context of WorkingFileSpace (in python code), whole subtree created by this instance is removed automatically

"""
import uuid
import os
import shutil
import logging
import json
import traceback

from ..notifications import send


class WorkingFileSpace:
    """The WorkingFileSpace context manager is used for the creation of temporary directory.

    The temporary directory is unique for every call of WorkingFileSpace object. After
    closing the context, all files are removed.

    Parameters:

        parent_dir (str) existing parent directory
        dirpath (str): path of currently created temporary directory
        dirname (str): directory name, last part of `dirpath` path
        userinfo (Any): any user defined data


    """
    TMP_DIR_ROOT = os.path.abspath(os.getenv('TMPDIR', '/tmp'))


    def __init__(self, parent_dir=None, dirname=None, userinfo=None, persistent=False, existing_dir=None, logger=None):
        """All parameters are optional.
        
        Args:
            parent_dir (str): Optional. Existing directory used as parent for new temporary directory.
            dirname (str): Optional. Name for new temporary directory. Default value is newly generated UUID4.
            userinfo (Any): Any user defined data.
            persistent (bool): Default is false, which means, directory is being removed when context exists.
            existing_dir (str): If this parameter is used, then directory path given in this parameter
                           is used as working directory and is not removed when context exits."""

        if parent_dir is None:
            parent_dir = WorkingFileSpace.TMP_DIR_ROOT

        self.logger = logger or logging.getLogger(__name__)

        if existing_dir:
            self.dirpath = existing_dir
            self.parent_dir, self.dirname = os.path.split(self.dirpath)
            self.persistent = True
        else:
            self.parent_dir = parent_dir
            self.dirname = dirname or str(uuid.uuid4())
            self.dirpath = os.path.join(self.parent_dir, self.dirname)
            self.persistent = persistent
        self.userinfo = {} if userinfo is None else userinfo

    def __enter__(self):
        dirs = os.listdir(self.parent_dir)
        if len(dirs)>=10:
            self._remove_oldest(dirs)
        os.makedirs(self.dirpath, exist_ok=False)
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.logger.debug(f'Removing temporary directory {self.dirpath}')
        if not self.persistent:
            self.will_remove_dirs(exc)
            shutil.rmtree(self.dirpath, ignore_errors=True)

    def _remove_oldest(self, dirs):
        o_time = -1
        o_name = None
        for d in dirs:
            full = os.path.join(self.parent_dir, d)
            c = os.stat(full).st_mtime
            if o_name is None or c < o_time:
                o_time = c
                o_name = d
        if o_name is not None:
            shutil.rmtree(os.path.join(self.parent_dir, o_name), ignore_errors=True)

    def will_remove_dirs(self, exc):
        """This function is called before removing whole directory tree."""
        send('workingfilespace-will-remove-dirs', {'dirpath': self.dirpath, 'userinfo': self.userinfo})

    def get_file_name(self, name=None):
        """Generates path for new file.

        File is not created. Only name is generated.

        Returns:
            New file name is joined to full path for current working directory.
        
        Args:
            name (str): Optional. If given, used as name of new file. If not given,
                     default value is UUID4 string."""
        if name is None:
            name = str(uuid.uuid4())
        return os.path.join(self.dirpath, name)

    def mkdir(self, name='tmp'):
        """Creates subdirectory directory in the filesystem.

        Args:
            name (str): the name of new subdirectory directory

        Returns:
            Full path of new directory.
        """
        dirname = self.get_file_name(name)
        os.makedirs(dirname, exist_ok=True)
        return dirname

    def write_json(self, filename, data):
        """Writes JSON file to the working directory.
        
        Args:
            filename (str): This should be only file name, not path.
            data (dict|list): User data, either Python dictionary, tuple or list.
        """
        with open(os.path.join(self.dirpath, filename), 'wt', encoding='utf8') as ifh:
            json.dump(data, fp=ifh, indent=4)

    def read_json(self, filename):
        """Reading JSON file from working directory.
        
        Args:
            filename (str): This should be only file name, not path.

        Returns:
            Python dictionary or list, depends on the content of JSON file.
        """
        full = os.path.join(self.dirpath, filename)
        if not os.path.exists(full):
            return None
        with open(full, 'rt', encoding='utf8') as filehandle:
            data = json.load(fp=filehandle)
        return data

    def write_text(self, filename, text):
        """Writes text file to the working directory.
        
        Args:
            filename (str): This should be only file name, not path.
            data (str): User data.
        """
        with open(os.path.join(self.dirpath, filename), 'wt', encoding='utf8') as ifh:
            ifh.write(text)

    def write_exception(self, filename:str):
        """Writes last exception to text file in the working directory.
        
        Args:
            filename (str): This should be only file name, not path.
        """
        with open(os.path.join(self.dirpath, filename), 'wt', encoding='utf8') as ifh:
            traceback.print_exc(file=ifh)

    def write_stacktrace(self, filename):
        """Writes last stacktrace to text file in the working directory.
        
        Args:
            filename (str): This should be only file name, not path.
        """
        with open(os.path.join(self.dirpath, filename), 'wt', encoding='utf8') as ifh:
            traceback.print_stack(file=ifh)

    def read_text(self, filename):
        """Reading text file from working directory.
        
        Args:
            filename (str): This should be only file name, not path.

        Returns:
            Content of file.
        """
        full = os.path.join(self.dirpath, filename)
        if not os.path.exists(full):
            return None
        with open(full, 'rt', encoding='utf8') as filehandle:
            text = filehandle.read()
        return text

