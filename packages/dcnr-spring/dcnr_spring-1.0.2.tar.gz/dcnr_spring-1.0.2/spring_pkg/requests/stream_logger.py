import logging
import io

class StreamLogger(logging.Logger):
    def __init__(self, name: str, level=logging.NOTSET):
        super().__init__(name, level)
        self._stream = io.StringIO()
        self._highest_level = logging.NOTSET
        self._stream_handler = logging.StreamHandler(self._stream)
        self._stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.addHandler(self._stream_handler)
        self.propagate = False  # Prevent messages from propagating to parent loggers

    def handle(self, record):
        # Update the highest log level used
        if record.levelno > self._highest_level:
            self._highest_level = record.levelno
        super().handle(record)

    def report(self, logger=None):
        """
        Returns all content logged using this logger and logs it to the standard logger
        with the highest log level used during the StreamLogger's usage.
        """
        content = self._stream.getvalue()
        if content:
            # Log the content to the standard logger
            standard_logger = logger
            if logger is None:
                standard_logger = logging.getLogger()
            standard_logger.log(self._highest_level, content)
        return content

    @property
    def highest_level(self):
        """Returns the highest log level used."""
        return self._highest_level