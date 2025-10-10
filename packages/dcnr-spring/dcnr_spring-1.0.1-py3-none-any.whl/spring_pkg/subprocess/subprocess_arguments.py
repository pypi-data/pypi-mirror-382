import pickle


class SubprocessArguments:
    def __init__(self, args:list, kwargs:dict):
        self.args = args
        self.kwargs = kwargs

    def to_file(self, filepath:str) -> str:
        with open(filepath, 'wb') as wft:
            pickle.dump(obj=self, file=wft)
    
    @staticmethod
    def from_file(filepath:str):
        with open(filepath,'rb') as rft:
            return pickle.load(file=rft)

