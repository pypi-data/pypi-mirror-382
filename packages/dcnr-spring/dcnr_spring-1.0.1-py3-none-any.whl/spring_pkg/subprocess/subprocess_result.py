import pickle


class SubprocessResult:
    def __init__(self, status:str, result:dict=None, error:str=None, type:str=None, stack:str=None, exception_obj:bytes=None):
        self.status = status
        self.result = result
        self.error = error
        self.type = type
        self.stack = stack
        self.exception_obj = exception_obj

    def to_file(self, filepath:str):
        with open(filepath, 'wb') as wft:
            pickle.dump(obj=self, file=wft)

    @staticmethod
    def from_file(filepath:str):
        with open(filepath,'rb') as rft:
            return pickle.load(file=rft)
