from .attribute import Attribute
from .many2one import Many2One
from .one2many import One2Many
from .function import Function
from .virtual import Virtual
from .field import Field
from .amount import Amount

__all__ = [Attribute, One2Many, Many2One, Virtual, Field, Amount]

def on_change(fields):
    from functools import wraps
    
    def decorator(func):
        setattr(func, 'on_changes', fields)

        @wraps(func)
        def wrapper(self, *arg, **kwargs):
            return func(self, *arg, **kwargs)
        return wrapper
    return decorator
