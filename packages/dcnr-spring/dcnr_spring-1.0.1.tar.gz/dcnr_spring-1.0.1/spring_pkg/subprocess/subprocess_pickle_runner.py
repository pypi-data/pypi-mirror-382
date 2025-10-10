"""
Subprocess manager for external language detection process.
"""

import subprocess
import pickle
import base64
import traceback
import os, io
import sys, uuid
import logging
import tempfile


from .subprocess_output_action import SubprocessOutputAction
from .subprocess_arguments import SubprocessArguments
from .subprocess_result import SubprocessResult


class SubprocessPickleRunner:
    """Manages external language detection process execution.
    
    Params:
    script_path (str): Path to the external script to run


    The external script should implement a main() function that uses SubprocessPickle 
    to read input from stdin and write output to stdout.
    The implementation itself has just one line. For example external script imports
    functiona named function_test. In this example the main function of external script should 
    execute this:

         SubprocessPickle(function_test).run()

    This handles all input/output and error handling.
    Remove execution is then done by calling:

        detector = SubprocessPickleRunner(script_path='path/to/external_script.py')
        detector.execute(arg1, arg2, kwarg1=value1, ....)

    Arguments to execute() are passed to the imported function in external script (in this example function_test).

    """
    
    def __init__(self, script_path:str):
        self.script_path = script_path
        self.input_data_path = None # name for temporary input data
        self.output_data_file_name = None # name for temporary output data
        self.python_executable = "python"
        self.last_results = None
        self.output_action = SubprocessOutputAction.ACTION_LOG
    
    def execute(self, *args, **kwargs):
        """
        Execute language detection in external process.
        
        Keys:
            file_path (str): Path to the file to analyze
            words_limit (int, optional): Word limit for analysis
            
        Returns:
            dict: Detection result or error information
            
        Raises:
            RuntimeError: If process execution fails
            <customerror>: If the original function raised an error
        """
        input_data = SubprocessArguments(list(args), dict(kwargs))
        exc_to_raise = None
        with tempfile.TemporaryDirectory() as temp_dir:
            self.input_data_path = os.path.join(temp_dir, 'input_data.pkl')
            self.output_data_file_name = os.path.join(temp_dir, 'output_data.pkl')

            input_data.to_file(self.input_data_path)

            try:
                result:SubprocessResult = self._run_subprocess()
                if result.status == 'SUCCESS':
                    return result.result
                elif result.status == 'ERROR':
                    self.last_results = result
                    # Try to re-raise the original exception if possible
                    if result.exception_obj is not None:
                        try:
                            exc_to_raise = pickle.loads(result.exception_obj)
                        except Exception:
                            exc_to_raise = ChildProcessError(result.error or 'Unknown error')
                else:
                    return result
                
            except subprocess.TimeoutExpired:
                raise RuntimeError("Subprocess timed out")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Subprocess failed: {e.stderr}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error in subprocess: {str(e)}")
            
            if exc_to_raise is not None:
                raise exc_to_raise
    
    def _get_console_output(self, stdout:str, stderr:str):
        return f'External process log {self.script_path}\nstdout: {stdout}\n\nExternal process stderr: {stderr}\n'

    def _run_subprocess(self, timeout=300):
        env_vars = dict(os.environ)
        env_vars['DCNR_SPRING_SUBPROCESS'] = '1'

        """Run the subprocess with input/output handling using pickle+base64."""
        process = subprocess.Popen(
            [self.python_executable, self.script_path, self.input_data_path, self.output_data_file_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env=env_vars
        )
        
        # Serialize input data using pickle + base64        
        stdout, stderr = process.communicate(timeout=timeout)
        
        if process.returncode != 0:
            self.last_results = SubprocessResult(
                status='ERROR',
                error=stderr or 'Unknown error',
                type='SubprocessError')
            raise subprocess.CalledProcessError(process.returncode, process.args, stderr=stderr)

        if self.output_action == SubprocessOutputAction.ACTION_LOG:
            logging.info(self._get_console_output(stdout, stderr))
        elif self.output_action == SubprocessOutputAction.ACTION_SAVE:
            self.console_output = self._get_console_output(stdout, stderr)

        try:
            output_bytes = SubprocessResult.from_file(self.output_data_file_name)
            return output_bytes
        except FileNotFoundError:
            self.last_results = SubprocessResult(
                status='ERROR',
                error='Output data file not found',
                type='SubprocessError')
            raise subprocess.CalledProcessError(process.returncode, process.args, stderr='Output data file not found')
        except Exception as x:
            self.last_results = SubprocessResult(
                status='ERROR',
                error=str(x),
                type='SubprocessError')
            raise subprocess.CalledProcessError(process.returncode, process.args, stderr='Output data file not found')

   
