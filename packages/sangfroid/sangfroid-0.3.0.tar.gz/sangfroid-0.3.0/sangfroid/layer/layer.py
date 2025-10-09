import copy
import logging
import bs4
import sangfroid.value as sv
from sangfroid.registry import Registry
from sangfroid.field import (
        Field,
        TagAttrField,
        ParamTagField,
        TagField,
        TypeNameField,
        SynfigVersionField,
        DescField,
        )
from sangfroid.util import (
        normalise_synfig_layer_type_name,
        type_and_str_to_value,
        type_and_value_to_str,
        )
from collections.abc import Callable
from typing import Self

logger = logging.getLogger('sangfroid')

class Layer:
    """
    Any layer in a Synfig file.

    This is the abstract superclass of all other kinds of layer.
    For example, Group, Text, and Animation are all subclasses
    of this class.
    """

    SYMBOL = '?' # fallback
    SYNFIG_VERSION = 0.0 # fallback

    type_   = TypeNameField()
    """The name Synfig uses internally for this type of layer.

    In Python, you must spell this as `type_`, because
    `type` is a reserved word."""

    version          = SynfigVersionField()
    """The earliest version of Synfig which will interpret
    the value of this field correctly."""

    active           = TagAttrField(bool,        True)
    "True if this layer is enabled."

    exclude_from_rendering = TagAttrField(
            bool,  False,
            name = 'exclude_from_rendering', # keep the underscores
            )
    "True if this layer should not be rendered."

    desc             = TagAttrField(str,         '')
    "A description of this layer."

    tag              = TagField()
    "The BeautifulSoup tag behind this item."

    desc             = DescField()
    "A description of this field. Can be None."

    ########################

    def __init__(self, tag=None):
        if tag is None:
            self._tag = self._construct_empty_tag()
        elif isinstance(tag, bs4.Tag):
            self._tag = tag
        else:
            raise TypeError(tag)

    @property
    def parent(self):
        cursor = self._tag.parent
        while cursor is not None:
            if cursor.name=='layer':
                return Layer.from_tag(cursor)
                return cursor
            cursor = cursor.parent

    def __repr__(self):
        result = '['
        result += ('-'*self.tag_depth)
        result += self.SYMBOL
        result += self.__class__.__name__.lower()
        try:
            desc = self.desc

            if desc:
                result += ' ' + repr(desc)
        except KeyError:
            pass

        result += ']'
        return result

    def __getitem__(self, f):
        found = self._tag.find('param', attrs={'name': f})
        if found is None:
            raise KeyError(f)
        return _name_and_value_of(found)[1]

    def __setitem__(self, f, val):
        found = self._tag.find('param', attrs={'name': f})
        if found is None:
            raise KeyError(f)
        old_value = _name_and_value_of(found)[1]

        if isinstance(val, sv.Value):
            if not isinstance(val, old_value.__class__):
                raise TypeError(val.__class__)

            new_value = val
        else:
            new_value = old_value.__class__(val)

        old_value.tag.replace_with(new_value.tag)

    def __contains__(self, f):
        found = self._tag.find(
                'param',
                attrs={'name': f},
                )
        return found is not None
    
    @property
    def tag_depth(self):
        cursor = self._tag.parent
        result = 0
        while cursor is not None:
            if cursor.name=='layer':
                result += 1
            cursor = cursor.parent
        return result

    def find_all(self,
                 *args:(bool|str|Self|Callable),
                 recursive:bool = True,
                 attrs:(dict|None) = None,
                 **kwargs,
                 ) -> [Self]:
        """
        Finds sub-layers with particular properties.

        This can only usefully be called on Groups. On other
        layers, it does nothing.

        Args:
            args: you may specify at most one positional argument.
                If it's True, all children will match.
                If it's False, no children will match.
                If it's a string, it will match on the "type" field.
                If it's the Layer class or one of its subclasses,
                    it will match layers of that type.
                If it's a callable, it will be called for each
                    child; if it returns True, the child will be
                    returned, and otherwise it won't.

            recursive: if this is False, we only search
                the layer's immediate children; if it's True,
                which is the default, we search all the layer's
                descendants.

            attrs: what to search for. We match against the
                field with the given name. The values should be
                strings, except that "type" can also be the class
                Layer or one of its subclasses.

        You may supply extra kwargs, under the same terms as
        "attrs"; you may not specify the same key in both.

        The format of the arguments is based on Beautiful Soup's
        Tag.find_all() method.
        """

        matching_special = None

        if len(args)>1:
            raise ValueError(
                    "You can only give one positional argument.")
        elif len(args)==1:

            if (
                    isinstance(args[0], str) or
                    (isinstance(args[0], type) and
                     issubclass(args[0], Layer))
                    ):
                if 'type' in kwargs:
                    raise ValueError(
                            "You can't give a type in both the positional "
                            "and keyword arguments.")

                kwargs['type'] = args[0]

            elif isinstance(args[0], bool):
                matching_special = args[0]

            elif hasattr(args[0], '__call__'):
                matching_special = args[0]

            else:
                raise TypeError(args[0])

        if 'attrs' in kwargs:
            for k,v in kwargs['attrs'].items():
                if k in kwargs:
                    raise ValueError("{k} specified both as a kwarg and in attrs")
                kwargs[k] = v

            del kwargs['attrs']

        for k,v in kwargs.items():
            if k=='type':
                if not isinstance(v, str):
                    v = v.__name__

                kwargs[k] = v.lower().replace('_', '')

        logger.debug("begin find_all")

        def matcher(found_tag):
            if found_tag.name!='layer':
                return False

            logger.debug("considering tag: %s %s",
                         found_tag.name, found_tag.attrs)

            found_layer = Layer.from_tag(found_tag)

            if matching_special is None:

                def munge(k,v):
                    if k=='type':
                        k = 'type_'
                        v = v.lower()

                    return (k,v)

                targets = [
                    munge(k,v)
                    for k,v in kwargs.items()
                    ]

                logger.debug("want: %s", targets)

                for k, want_value in targets:
                    try:
                        found_value = getattr(found_layer, k)
                        logger.debug("  -- %s field is %s; want %s", k,
                                     repr(found_value),
                                     repr(want_value),
                                     )
                    except AttributeError:
                        logger.debug("  -- it does not have a %s", k)
                        continue

                    logger.debug("  want: %s  found: %s",
                                 want_value, found_value)

                    if found_value==want_value:
                        logger.debug("    -- a match!")
                        return True

                logger.debug("  -- no matches.")
                return False

            elif isinstance(matching_special, bool):
                return matching_special

            else:
                result = matching_special(found_tag)
                logger.debug("  -- callback says: %s", result)
                return result

            raise ValueError(found_tag)

        result = [
                self.from_tag(x) for x in
                self._tag.find_all(matcher,
                                  recursive=recursive,
                                  )
                ]
        logger.debug("find_all found: %s",
                     result,
                     )

        return result

    @property
    def children(self) -> [Self]:
        """
        The sub-layers of this layer.

        This is a generator. If this layer is not a Group,
        it yields no objects.
        """
        return
        yield

    def find(self,
             *args:(bool|str|Self|Callable),
             recursive:bool = True,
             attrs:(dict|None) = None,
             **kwargs,
             ) -> (Self|None):
        """
        Like find_all(), except that it only returns the first item.
        
        If no items are found, it returns None.

        Arguments are as for find_all().
        """
        items = self.find_all(
                *args,
                recursive=recursive,
                attrs=attrs,
                **kwargs,
                )
        if items:
            return items[0]
        else:
            return None

    __call__ = find

    ########################

    """
    Which Layer subclass handles which type of <layer> tag.
    """
    handles_type = Registry()

    @classmethod
    def from_tag(cls, tag:bs4.Tag) -> Self:
        """
        Constructs a layer from an XML tag.
        """
        tag_type = tag.get('type', None)
        if tag_type is None:
            raise ValueError(
                    f"tag has no 'type' field: {tag}")
        return cls.handles_type.from_name(name=tag_type)(tag)

    def _as_dict(self):
        return dict([
            _name_and_value_of(param)
            for param in self._tag.find_all('param',
                                            recursive=False,
                                            )
            ])

    def items(self):
        return self._as_dict().items()

    def keys(self):
        return self._as_dict().keys()

    def values(self):
        return self._as_dict().values()

    def __iter__(self):
        return self.children.__iter__()

    @classmethod
    def _construct_empty_tag(cls):
        result = bs4.Tag(name='layer')
        result.append("\n")

        for c in cls.mro():
            for field in c.__dict__.values():
                if isinstance(field, Field):
                    field.__set_name__(cls, field.name)
                    if isinstance(field, TagAttrField):
                        value = field.default
                        if value is None:
                            continue
                        elif isinstance(value, str):
                            if value=='':
                                continue
                        elif isinstance(value, bool):
                            value = str(value).lower()
                        else:
                            value = str(value)

                        result[field.name] = value

                    elif isinstance(field, ParamTagField):
                        param = bs4.Tag(name="param")
                        param['name'] = field.name

                        type_ = field.type_

                        if issubclass(type_, sv.Time):
                            type_ = _TimeButString

                        param_default = type_(field.default)
                        param.append(param_default._tag)
                        result.append(param)
                        result.append("\n")

        return result

    def __len__(self):
        return len(self._sublayer_tags())

    def append(self, layer: Self):
        """
        Adds a Layer to the end of a Group.

        Synfig stores layers backwards, so this will result in the layer
        appearing in the file before all other layers of its group.

        Args:
            layer: the layer to add

        Raises:
            NotImplementedError: if you're trying to add a layer
                to a layer which isn't a Group.
        """
        raise NotImplementedError(
                "Only Groups can contain other layers.")

    def _sublayer_tags(self):
        return self._tag.find_all('layer')

def _name_and_value_of(tag):
    if tag.name!='param':
        raise ValueError(f"param is not a <param>: {tag}")

    name = tag.get('name', None)
    if name is None:
        raise ValueError(f"param has no 'name' field: {tag}")

    value_tags = [tag for tag in tag.children
                  if isinstance(tag, bs4.element.Tag)
                  ]

    if len(value_tags)!=1:
        raise ValueError(f"param should have one value: {tag}")

    value_tag = value_tags[0]

    value = sv.Value.from_tag(value_tag)
    return name, value

class _TimeButString(sv.Time):
    """
    Same as sangfroid.value.Time, except the type of its value is str.

    This is an ugly hack. Layer._construct_empty_tag() instantiates
    a Value subclass ephemerally, in order to get its tag. If we do
    this with Time, the default value will be run through T(), and
    since the tag being constructed is empty, T() will have no way
    to get the FPS, and so no way to interpret default times which
    are specified in seconds.

    Thus, we have this subclass of sv.Time with a type of str,
    so that T() doesn't see the value on the way through.
    """
    our_type = str

    @classmethod
    def get_name_for_tag(cls):
        return 'time'

__all__ = [
        'Layer',
        ]
