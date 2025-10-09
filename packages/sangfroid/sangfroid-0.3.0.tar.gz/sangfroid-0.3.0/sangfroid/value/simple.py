"""
Values based directly on Python types.
"""
from sangfroid.value.value import Value
from sangfroid.t import T
import warnings

class Simple(Value):
    """
    Abstract superclass of `Value`s which are based directly on Python
    builtin types.

    Issue:
        Subclasses of `Simple` should coerce freely to and from their
        builtin types, but they don't. See issue
        [#14](https://gitlab.com/marnanel/sangfroid/-/issues/14).

    Properties:
        our_type (type): the Python type we're based on.
    """
    our_type = None

    @property
    def value(self):
        if self.our_type is None:
            raise NotImplementedError()

        result = self._tag.get('value', None)
        if result is None:
            raise ValueError(
                    f"This tag should have had a 'value' attribute, "
                    f"but it didn't:\n\n"
                    f"{self._tag}")
        assert isinstance(result, str), f"{result} {type(result)} {self._tag} {type(self._tag)}"

        result = self._construct_value(result)

        return result

    def _construct_value(self, v):
        return self.our_type(v)

    @value.setter
    def value(self, v):
        if self.our_type is None:
            raise NotImplementedError()

        if v==() or v is None:
            result = self.our_type()

        else:
            try:
                result = self.our_type(v)
            except TypeError:
                raise TypeError("I need a value of type "
                                f"{self.our_type.__name__}, "
                                "not "
                                f"{v.__class__.__name__}."
                                )

        result = self._value_to_str(result)

        self._tag.name = self.get_name_for_tag()
        self._tag.attrs = {
                'value': result,
                }
        self._tag.clear()

    @classmethod
    def _value_to_str(cls, v):
        return str(v)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            v = other.value
        else:
            try:
                v = self.our_type(other)
            except ValueError:
                v = other

        return self._compare_with(v)

    def _compare_with(self, v):
        return self.value==v

class Numeric(Simple):
    """
    Abstract superclass of Values based on numbers.
    """
    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

@Value.handles_type()
class Real(Numeric):
    """
    Values based on real numbers.

    Property:
        NEAR_AS_DAMMIT (float): two `Real`s will compare as equal
            if they differ by this amount or less.
    """

    NEAR_AS_DAMMIT = 0.0001
    our_type = float

    def _compare_with(self, v):
        try:
            return abs(self.value-v)<=self.NEAR_AS_DAMMIT
        except TypeError:
            return False

    @classmethod
    def _value_to_str(cls, v):
        return '%.010f' % (v,)

@Value.handles_type()
class Integer(Numeric):
    """
    Values based on integers.
    """
    our_type = int

    def __int__(self):
        return self.value

@Value.handles_type()
class Bool(Simple):
    """
    Values based on booleans.
    """
    our_type = bool

    def __bool__(self):
        return self.value

    def _construct_value(self, v):
        assert isinstance(v, str)
        if v.lower()=='true':
            return True
        elif v.lower()=='false':
            return False
        else:
            warnings.warn(
                    "boolean string should have been 'true' or 'false', "
                    f"but it was {repr(v)}; treating as False.")
            return False

    @classmethod
    def _value_to_str(cls, v):
        return str(v).lower()

@Value.handles_type()
class Angle(Simple):
    """
    Values representing angles, which are based on floats.

    The angles are measured in degrees.

    Puzzled:
        This doesn't seem like it should be a `Simple`.
    """
    our_type = float

    def _str_inner(self):
        return '%g°' % (self.value,)

    def as_python_expression(self):
        v = self.value
        return str(v)

    def __float__(self):
        return self.value

@Value.handles_type()
class Time(Simple):
    """
    A Value based on the time type, `T`.

    We don't provide __float__ and __int__ here because
    they'd be ambiguous between frames and seconds.

    Puzzled:
        Why is this a `Simple`? It's not based on a
        Python builtin class.
    """
    our_type = T

    def _construct_value(self, v):
        return self.our_type(
                v,
                ref = self._tag,
                )

    def as_python_expression(self):
        v = self.value

        if v==0:
            return '0'
        else:
            return repr(str(v))
