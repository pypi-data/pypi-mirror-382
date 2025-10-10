"""
Function that checks whether all provided arguments are non-falsy.

Example:
    is_set(param_x, param_y)
    This will return True if BOTH params are truthy (not None, False, 0, '').
"""
def is_set(*args):
    return all(arg is not None for arg in args)