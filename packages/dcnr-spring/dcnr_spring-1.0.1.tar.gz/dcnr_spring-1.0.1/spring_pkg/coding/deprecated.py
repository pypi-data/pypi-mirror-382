
import warnings
import functools

def deprecated(reason: str):
    """
    Marks function as deprtecated in the code.
    
    # Example usage:
    @deprecated("use new_function() instead")
    def old_function(...):
        # Old function.

        # .. deprecated:: 1.2.0
        #   Use :func:`new_function` instead.
        #
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"{func.__name__} is deprecated: {reason}",
                          DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

