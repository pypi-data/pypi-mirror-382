import pickle
from .stream_logger import StreamLogger

class MessageServiceClient():
    def __init__(self, uploader_user:str=None, correlation_id:str=None, job_id:str=None, user_data:any=None):
        self.uploader_user = uploader_user
        self.correlation_id = correlation_id
        self.job_id = job_id
        self.user_data = user_data
        self.logger = StreamLogger(name=f"MessageServiceClient-{self.correlation_id}")

    def __getstate__(self):
        """Exclude logger from pickling."""
        state = self.__dict__.copy()
        if 'logger' in state:
            del state['logger']
        return state

    def __setstate__(self, state):
        """Restore state and recreate logger."""
        self.__dict__.update(state)
        self.logger = StreamLogger(name=f"MessageServiceClient-{self.correlation_id}")

    def complete_job(self, data):
        pass

    def fail_job(self, error):
        pass

    def send_back(self, data):
        pass

    def send_error(self, error):
        pass

    def complete_message(self):
        pass

    def get_async_producer(self):
        return pickle.dumps(self)
    
