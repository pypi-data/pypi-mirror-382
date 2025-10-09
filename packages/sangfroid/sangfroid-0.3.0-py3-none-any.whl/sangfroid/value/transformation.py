import bs4
from sangfroid.value.value import Value
from sangfroid.value.simple import Angle
from sangfroid.value.vector import X_Y
from copy import copy

@Value.handles_type()
class Composite(Value):

    REQUIRED_KEYS = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.REQUIRED_KEYS is None:
            raise NotImplementedError()

    @classmethod
    def _get_empty_tag(cls):
        result = bs4.element.Tag(name='composite')
        result['type'] = cls.get_name_for_tag()
        return result

    @property
    def value(self):
        def name_and_value(n):

            name = n.name

            assert name!='layer'

            value_tags = [v
                 for v in n.children
                 if isinstance(v, bs4.element.Tag)
                 ]

            if len(value_tags)!=1:
                raise ValueError("Fields in composite types should only "
                                 f"have a single value: {n}")

            value = Value.from_tag(value_tags[0])

            return name, value

        result = dict(
                [name_and_value(field)
                 for field in self._tag.children
                 if isinstance(field, bs4.element.Tag)
                 ])

        if self.REQUIRED_KEYS is not None:
            assert result.keys()==self.REQUIRED_KEYS.keys()

        return result

    @value.setter
    def value(self, new_value):
        if not hasattr(new_value, 'items'):
            raise TypeError("The new value must be a dict.")

        for k,v in new_value.items():
            if self.REQUIRED_KEYS is not None:
                if k not in self.REQUIRED_KEYS:
                    raise KeyError(
                    f"{k} is not one of the keys we can accept. "
                    f"We can accept: "
                    f"{' '.join(sorted(self.REQUIRED_KEYS.keys()))}")

        self.tag.clear()

        for remaining, v in new_value.items():

            v_as_value = self.REQUIRED_KEYS[remaining](v)

            new_subtag = bs4.Tag(name=remaining)
            new_subtag.append(copy(v_as_value.tag))
            new_subtag.append("\n")
            self.tag.append(new_subtag)

    def __getattr__(self, key):
        result = self.get(key, default=None)

        if result is None:
            raise AttributeError(key)

        return result

    def __getitem__(self, key):
        result = self.get(key=key, default=None)
        if result is None:
            raise KeyError(key)
        return result

    def get(self, key, default=None):
        found = [v
                 for v in self._tag.children
                 if isinstance(v, bs4.element.Tag)
                 and v.name==key
                 ]

        if len(found)==0:
            return default
        elif len(found)>1:
            raise ValueError(f"multiple values for {key}!")

        values = [v
                 for v in found[0].children
                 if isinstance(v, bs4.element.Tag)
                 ]

        if len(values)==0:
            return default
        elif len(values)>1:
            raise ValueError(f"multiple values for {key}!")
        elif values[0]==None:
            return default
        else:
            return Value.from_tag(values[0])

    def keys(self):
        # No point constructing all the values
        return [v.name
                 for v in self._tag.children
                 if isinstance(v, bs4.element.Tag)
                 ]

    def values(self):
        return self.value.values()

    def items(self):
        return self.value.items()

    def __len__(self):
        return len([v
                 for v in self._tag.children
                 if isinstance(v, bs4.element.Tag)
                 ])

    def __eq__(self, other):

        if not hasattr(other, 'items'):
            return False

        if len(other)!=len(self):
            return False

        for key, value in self.items():
            if other[key]!=value:
                return False

        return True

    def as_python_expression(self):
        value = self.value

        result = '{\n'
        for f,v in value.items():
            result += '     %40s: %s,\n' % (
                    repr(f),
                    v.as_python_expression(),
                    )
        result += (' '*36) + '}'

        return result

    @classmethod
    def _subfields(cls):
        return set(cls.REQUIRED_KEYS or ())

    @classmethod
    def _construct_from(cls, tag):
        try:
            subtype = tag['type']
        except KeyError:
            raise KeyError(
                    'This <composite> layer has no type parameter. '
                    'You probably wanted type="transformation".'
                    )

        if subtype.lower()=='transformation':
            return Transformation(tag)
        else:
            raise KeyError(
                    f'This <composite> layer has type="{subtype}", '
                    'which isn\'t a type I know.\n'
                    'You probably wanted type="transformation".'
                    )

class Transformation(Composite):
    REQUIRED_KEYS = {
            'offset': X_Y,
            'angle': Angle,
            'skew_angle': Angle,
            'scale': X_Y,
            }
