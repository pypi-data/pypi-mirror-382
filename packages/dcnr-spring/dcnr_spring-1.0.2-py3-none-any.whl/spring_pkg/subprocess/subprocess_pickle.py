import sys
import traceback
import pickle

from .subprocess_arguments import SubprocessArguments
from .subprocess_result import SubprocessResult


class SubprocessPickle():
    def __init__(self, function:callable):
        self.function = function
        self.input_file_name = None
        self.output_file_name = None

    def run(self):
        if self.function is not None:
            print('SubprocessPickle.run ', self.function.__name__)
        try:
            self.input_file_name = sys.argv[1]
            self.output_file_name = sys.argv[2]

            # Read input from stdin as base64-encoded pickle
            input_data = SubprocessArguments.from_file(self.input_file_name)
            
            # Execute function
            result = self.function(*input_data.args, **input_data.kwargs)
            
            # Write result to stdout as base64-encoded pickle
            self.handle_success(result)
            
        except Exception as e:
            print('SubprocessPickle.run exception')
            print(e)
            traceback.print_exc()
            # Write error to stderr as base64-encoded pickle and exit with non-zero code
            self.handle_exception(e)

        # TODO: try without shutdown_service
        # import dcnr_spring as spring
        # spring.notifications.shutdown_service()
        sys.exit(0)
      
    def handle_exception(self, e:Exception):
        error_result = SubprocessResult(
            status='ERROR',
            error=str(e),
            type=type(e).__name__,
            stack=traceback.format_exc(),
            exception_obj=pickle.dumps(e)
        )
        error_result.to_file(self.output_file_name)

    def handle_success(self, result:dict):
        success_result = SubprocessResult(
            status='SUCCESS',
            result=result
            )
        success_result.to_file(self.output_file_name)
