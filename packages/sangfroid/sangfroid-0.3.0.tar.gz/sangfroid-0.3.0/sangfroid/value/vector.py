import bs4
from sangfroid.value.value import Value

@Value.handles_type()
class Vector(Value):

    # it may happen that other types occur, though I don't
    # know of any at present, or how we could know if they
    # applied to us
    our_type = float

    TAG_NAME = 'vector'
    FIELDS = ['x', 'y']

    @property
    def value(self):
        return dict(
                [(field.name,
                  field.string)
                 for field in self._tag.children
                 if isinstance(field, bs4.element.Tag)
                 ])

    def _raise_type_error(self):
        raise TypeError(
                "Vectors may be constructed as "
                f"{self.__class__.__name__}"
                f"({','.join(self.FIELDS)}), or "
                f"{self.__class__.__name__}"
                "(dict_of_members).")

    def __getattr__(self, f):
        if f.startswith('_'):
            raise AttributeError(f)

        s = self._tag.find(name=f)
        if s is None:
            raise AttributeError(f)
        v = self.our_type(s.text)
        return v

    @value.setter
    def value(self, v):

        if v is None:
            members = {}
        elif isinstance(v, tuple):
            if len(v)==0:
                members = {}
            elif len(v)==2:
                members = dict(zip(self.FIELDS, v))

                for m in members.values():
                    if not isinstance(m, (float, int)):
                        self._raise_type_error()

            else:
                self._raise_type_error()
        elif hasattr(v, 'items'):
            members = v
        else:
            self._raise_type_error()

        self._tag.name = self.TAG_NAME
        self._tag.attrs = {}

        for k, v in members.items():
            addendum = bs4.element.Tag(name=k)
            if isinstance(v, float):
                addendum.string = '%.010f' % (v,)
            else:
                addendum.string = str(v)
            self._tag.append(addendum)

    def __getitem__(self, key):
        result = self.get(key, default=None)

        if result is None:
            raise KeyError(key)

        return result

    def get(self, key, default=None):
        if isinstance(key, int):
            key = self.keys()[key]

        v = [field.string
             for field in self._tag.children
             if isinstance(field, bs4.element.Tag)
             and field.name==key
             ]

        if len(v)==0:
            return default

        return self.our_type(v[0])

    # FIXME: All these methods are written in terms of self.value,
    # which is inefficient because all the values must be created
    # every time. They should be fixed to read self._tag themselves.

    def keys(self):
        return sorted(self.value.keys())

    def values(self):
        if self.is_animated:
            return None
        return [self.our_type(v) for v in self.value.values()]

    def items(self):
        return [(k, self.our_type(v)) for k,v in self.value.items()]

    def __len__(self):
        return len(self.value)

    def as_tuple(self):
        return tuple(
                [self.our_type(self.value[k])
                 for k in sorted(self.value.keys())]
                )

    def _str_inner(self):
        if sorted(self.value.keys())==['x', 'y']:
            return str(self.as_tuple())
        else:
            return str(self.value)

    def __eq__(self, other):
        try:
            if len(other)!=len(self):
                return False
        except TypeError:
            return False

        return all([left==right for left,right in zip(self, other)])

    def __iter__(self):
        for v in self.values():
            yield v

    def _get_empty_tag(cls):
        return super()._get_empty_tag(cls.TAG_NAME)

    @classmethod
    def _construct_from(cls, tag):

        def first_child_tag(t):
            tags = [n for n in t.children if isinstance(n, bs4.Tag)]
            if len(tags)==0:
                return None
            else:
                return tags[0]

        c = None
        start_tag = tag

        if tag.name==cls.ANIMATED:
            waypoint_tag = first_child_tag(tag)
            if waypoint_tag is None:
                # no way of telling; make the best guess
                c = X_Y
            else:
                start_tag = first_child_tag(waypoint_tag)

        if c is None:
            fields = set([
                f.name for f in start_tag.children
                if isinstance(f, bs4.Tag)
                ])

            if fields=={'x', 'y'}:
                c = X_Y
            else:
                raise TypeError(
                        "This tag isn't a vector type I know:\n"
                        f"  the fields are: {repr(fields)}.\n"
                        f"{tag}"
                        )

        assert c is not None
        return c(tag)

class X_Y(Vector):
    pass
