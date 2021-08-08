import facho.model as model
import facho.model.fields as fields

from datetime import date, datetime

__all__ = ['Element', 'Name', 'Date', 'Time', 'Period', 'ID']

class Element(model.Model):
    """
    Lo usuamos para elementos que solo manejan contenido
    """
    __name__ = 'Element'
    
class Name(model.Model):
    __name__ = 'Name'

class Date(model.Model):
    __name__ = 'Date'

    def __default_set__(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, date):
            return value.isoformat()

    def __str__(self):
        return str(self._value)

class Time(model.Model):
    __name__ = 'Time'

    def __default_set__(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, date):
            return value.strftime('%H:%M:%S-05:00')

    def __str__(self):
        return str(self._value)

class Period(model.Model):
    __name__ = 'Period'

    start_date = fields.Many2One(Date, name='StartDate', namespace='cbc')

    end_date = fields.Many2One(Date, name='EndDate', namespace='cbc')

class ID(model.Model):
    __name__ = 'ID'

    def __default_get__(self, name, value):
        return self._value

    def __str__(self):
        return str(self._value)
