from .attribute import Attribute
from .many2one import Many2One
from .model import Model
from .function import Function
from .virtual import Virtual
from .field import Field

__all__ = [Attribute, Many2One, Model, Virtual, Field]

def on_change(fields):
    from functools import wraps
    
    def decorator(func):
        setattr(func, 'on_changes', fields)

        @wraps(func)
        def wrapper(self, *arg, **kwargs):
            return func(self, *arg, **kwargs)
        return wrapper
    return decorator
