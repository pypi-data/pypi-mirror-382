from ..coding.locked_status import LockedValue

_test_g_mode = LockedValue[bool](False)

def set_test_mode(value):
    _test_g_mode.set(value)

def get_test_mode():
    return _test_g_mode.get()
