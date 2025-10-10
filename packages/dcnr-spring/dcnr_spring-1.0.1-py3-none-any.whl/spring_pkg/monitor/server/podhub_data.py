class PodHubData:
    def __init__(self, **kwargs):
        self.application = kwargs.get('application')
        self.instance = kwargs.get('instance')
        self.instance_status = kwargs.get('instance_status')
        self.start_time = kwargs.get('start_time')
        self.received = kwargs.get('received')