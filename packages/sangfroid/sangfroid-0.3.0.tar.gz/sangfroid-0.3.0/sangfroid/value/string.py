import bs4
from sangfroid.value.value import Value
from sangfroid.t import T

@Value.handles_type()
class String(Value):
    our_type = str

    @property
    def value(self):
        result = str(self._tag.string)
        return result

    @value.setter
    def value(self, v):
        self._tag.string = str(v)

    def as_python_expression(self):
        return repr(self.value)
