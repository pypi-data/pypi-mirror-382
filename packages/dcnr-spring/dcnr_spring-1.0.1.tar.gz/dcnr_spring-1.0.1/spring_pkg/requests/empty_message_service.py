from .message_request_client import MessageServiceClient


class EmptyMessageService(MessageServiceClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.send_back_value = None
        self.send_error_value = None
        self.message_completed = False

    def complete_job(self, data):
        self.send_back_value = data
        self.message_completed = True

    def fail_job(self, error):
        self.send_error_value = error
        self.message_completed = True

    def send_back(self, data):
        self.complete_job(data)

    def send_error(self, error):
        self.fail_job(error)

    def complete_message(self):
        self.message_completed = True
