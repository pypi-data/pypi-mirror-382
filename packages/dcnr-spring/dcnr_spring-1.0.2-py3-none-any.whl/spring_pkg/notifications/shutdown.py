from ..coding.locked_status import LockedValue

_should_shut_down = LockedValue[bool](False)


def shutdown_service():
    """ Mark the service as shutting down. """
    _should_shut_down.set(True)

def is_shutting_down():
    """ Check if the service is marked as shutting down. """
    return _should_shut_down.get()

