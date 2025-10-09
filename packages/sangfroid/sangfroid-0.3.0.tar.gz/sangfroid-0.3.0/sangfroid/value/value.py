import copy
import bs4
import functools
import copy
from sangfroid.registry import Registry
from sangfroid.t import T
from typing import Self, Any

class Value:
    """
    The abstract superclass of all Values.
    """

    ANIMATED = 'animated'

    def __init__(self, *args):

        if len(args)==1 and isinstance(args[0], bs4.element.Tag):
            self._tag = args[0]
        else:
            self._tag = self._get_empty_tag()
            if len(args)==1:
                self.value = args[0]
            else:
                self.value = args

        assert self._tag is not None

    @classmethod
    def _get_empty_tag(cls, name:str=None) -> bs4.Tag:
        name = name or cls.get_name_for_tag()
        result = bs4.Tag(name=name)
        return result

    @property
    def tag(self) -> bs4.Tag:
        return self._tag

    @property
    def is_animated(self) -> bool:
        """
        Whether the value is animated.
        """
        return self._tag.name==self.ANIMATED

    @is_animated.setter
    def is_animated(self, v:bool):
        self._set_animated(v)

    def _set_animated(self,
                      whether:bool,
                      adjust_contents:bool = True,
                      ):
        """
        Sets the `Value` to be animated or not animated.

        # How we determine the new value, when `adjust_contents` is `True`

        If `whether` is `True`, the value will gain a timeline
        containing a single `Waypoint` at time 0,
        with our current value as its value, and `before` and `after`
        both set to `"clamped"`.

        If `whether` is `False`, its new value will be equal to the
        earliest `Waypoint` on its former timeline.

        Issue:
            In this case we *should* raise the exception ourselves;
            at present we just cause an indexing error by
            dereferencing the timeline.

        Args:
            whether: if `True`, the `Value` will be marked as animated.
                If `False`, it will be marked as not animated.
                If this would result in no change, nothing happens.

            adjust_contents: if `True`, the value after this call
                will be based on the value before this call; see above
                for the details. If it's `False`, the caller takes
                responsibility for fixing up the value.

        Raises:
            IndexError: when `adjust_contents` is `True`, `whether` is False`,
                and there are no `Waypoints` on our current Timeline.
        """
        whether = bool(whether)

        if whether==self.is_animated:
            pass
        elif whether:

            if adjust_contents:
                former_value = self.value

            our_type = self._tag.name
            self._tag.attrs = {}
            self._tag.name = self.ANIMATED
            self._tag['type'] = our_type

            if adjust_contents:
                self._tag.clear()
                self.timeline[0] = former_value
        else:

            if adjust_contents:
                timeline = self.timeline
                first_value = timeline.values()[0]
            else:
                first_value = None

            self._tag.clear()

            new_tag = self._get_empty_tag()
            self._tag.replace_with(new_tag)
            self._tag = new_tag

            if first_value is not None:
                old_tag = self._tag

                self._tag = copy.deepcopy(first_value.value._tag)
                if old_tag.parent is not None:
                    old_tag.replace_with(self._tag)

    @property
    def timeline(self) -> 'Timeline':
        """
        Our timeline, showing how our value changes over time.

        If we're not animated, the timeline will be empty.

        `Timeline` objects hold no state of their own except a reference back to
        their parent `Value`. So this call constructs a new `Timeline` instance
        every time.
        """

        result = Timeline.__new__(Timeline)
        result.parent = self
        return result

    @timeline.setter
    def timeline(self, v: 'Timeline'):

        if isinstance(v, list) and all([n for n in v if isinstance(n, Waypoint)]):
            self._set_waypoints(copy.deepcopy(v))
        elif isinstance(v, dict):
            self.timeline = list(v.values())
        elif isinstance(v, Timeline):
            if v.parent is self:
                return
            self._set_waypoints(copy.deepcopy(v.values()))
        else:
            raise TypeError("A timeline can only be set to another timeline or "
                            "a dict or list of Waypoints.")

    def _waypoint_tags(self) -> [bs4.Tag]:
        """
        A list of Beautiful Soup tags of waypoints on our timeline.

        The list is in the same order it appears in the file.
        If we're not animated, the list will have no members.

        Returns:
            list of Tag
        """

        if self._tag.name!=Value.ANIMATED:
            return []

        result = [wt for wt in self._tag
                  if isinstance(wt, bs4.element.Tag)]

        return result

    def _waypoints(self) -> {T: 'Waypoint'}:
        """
        A dict of Waypoints on our timeline.

        If we're not animated, the dict will have no members.
        """

        waypoints = self._waypoint_tags()

        if not waypoints:
            return {}

        our_type = self._tag['type']

        values = [Waypoint.from_tag(wt,
                                    our_type = our_type,
                                    )
                  for wt in waypoints]

        result = dict([(v.time, v) for v in values])

        return result

    def _set_waypoints(self, v: ['Waypoint']):
        """
        Sets our timeline to contain exactly the given sequence of waypoints.

        They will be stored sorted, with newlines between them.

        This necessarily involves setting whether we're animated.

        Args:
            v: the waypoints.
        """

        if not v:
            self._set_animated(
                    whether = False,
                    )
            return

        self._set_animated(
                whether = True,
                adjust_contents = False,
                )
        self._tag.clear()

        v_for_ordering = dict([
            (
                T(wp.tag['time'], ref=self.tag),
                wp
                )
                for wp in v
            ])

        for i, (time, w) in enumerate(sorted(v_for_ordering.items())):
            if i!=0:
                self._tag.append('\n')
            self._tag.append(w.tag)

    def __len__(self):
        return len(self._waypoints())

    @property
    def our_type(self) -> str:
        """
        The name of the Synfig layer type.

        For example, 'circle' or 'group'.
        """
        result = self._tag.name
        if result==Value.ANIMATED:
            result = self._tag['type']

        return result

    def _str_inner(self):
        return str(self.value)

    def __str__(self):
        if self.is_animated:
            return '(animated)'
        else:
            return self._str_inner()

    def __repr__(self):
        return '['+self.__class__.__name__+' '+str(self)+']'

    @classmethod
    def _subfields(cls):
        """
        Returns a set of names of keys
        generally found within values of this class.

        Used by sangfroid.layer.include_shortcuts().

        Returns:
            set
        """
        return set()

    @property
    def value(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if isinstance(other, Value):
            return self.value == other.value

        return self.value == other

    def as_python_expression(self) -> str:
        """
        A Python expression which could be passed to the constructor
        of this class in order to recreate this value.

        Used by `etc/pick-and-mix-to-layers.py`.
        """
        return str(self)

    @classmethod
    def get_name_for_tag(cls) -> str:
        return cls.__name__.lower()

    ########################

    # Factories, and setup for factories

    handles_type = Registry()

    @classmethod
    def from_tag(cls,
                 tag: bs4.Tag,
                 ) -> Self:
        """
        Given a Beautiful Soup tag, returns an instance of an appropriate
        subclass of `Value`, representing it.

        Args:
            tag: the Beautiful Soup tag.

        Raises:
            KeyError: if there's no known subclass of `Value` to represent
                that tag.
            ValueError: if the tag is animated, but not marked with a type.
        """

        if tag.name==cls.ANIMATED:

            type_name = tag['type']
            if type_name is None:
                raise ValueError(f"Animated values need a type: {tag}")

        else:
            type_name = tag.name

        result_type = cls.handles_type.from_name(name=type_name)
        result = result_type._construct_from(tag)

        return result

    @classmethod
    def _construct_from(cls, tag:bs4.Tag) -> Self:
        return cls(tag)

#######################

class Timeline:
    r"""
    How a Value changes over time.

    This class can't be created directly; it should only be created by
    a Value. It holds no state of its own, other than the reference
    to the Value which created it.

    Attributes:
        parent (Value): the Value which created this Timeline
    """

    def __init__(self):
        raise NotImplementedError(
                "Don't construct timelines directly."
                )

    def __iter__(self):
        for t,w in sorted(self.parent._waypoints().items()):
            yield w

    def _ensure_fps(self, t: (int|float|str|T)):
        if isinstance(t, (int, float, str)):
            return T(t, ref = self.parent._tag)
        elif isinstance(t, T):
            if t._fps is None:
                return T(t._frames, self.parent._tag)
            else:
                return t
        else:
            raise TypeError("I need T, or an int, float, str to create a T. "
                    f"You gave me {type(t)}.")

    def keys(self):
        return list(self.parent._waypoints().keys())

    def values(self):
        return list(self.parent._waypoints().values())

    def items(self):
        return list(self.parent._waypoints().items())

    def __iadd__(self, waypoints:['Waypoint']):
        self.add(waypoints,
            overwrite = True,
                 )
        return self

    def add(self,
            waypoints:['Waypoint'],
            overwrite:bool = False,
            ) -> Self:
        """
        Adds a Waypoint, or a set of Waypoints, to this Timeline.

        Args:
            waypoints: the Waypoint (or the list of Waypoints) to add.
            overwrite: if `True`, new Waypoints will replace existing
                Waypoints with the same times. Otherwise, if new Waypoints
                clash with existing Waypoints, we raise `ValueError`.

        Raises:
            ValueError: if `overwrite` is `False`, but `waypoints` contains
                waypoints which clash with waypoints already on our timeline.
            TypeError: if `waypoints` is neither a Waypoint nor a
                list of Waypoints; or if a listed Waypoint has a tag
                which isn't a `bs4.Tag`.
        """

        def raise_argument_error():
            raise TypeError(
                    "The argument to add() "
                    "must be either a Waypoint or a list of Waypoints.")

        if isinstance(waypoints, Waypoint):
            waypoints = [waypoints]
        elif isinstance(waypoints, list):
            pass
        else:
            raise_argument_error()

        # check they're sensible
        for w in waypoints:
            if not isinstance(w, Waypoint):
                raise_argument_error()
            elif not isinstance(w.tag, bs4.Tag):
                raise TypeError(
                        f'{w} has a tag of type {type(w.tag)}')

        def fix_up_times(wps):
            return dict([
                (T(wp.tag['time'], ref=self.parent.tag).frames, wp)
                for wp in wps])

        existing = fix_up_times(self.parent._waypoints().values())
        newcomers = fix_up_times(waypoints)

        clashes = [
            (oldtime, newtime)
                for oldtime, old in existing.items()
                for newtime, new in newcomers.items()
                if oldtime==newtime
                ]

        if overwrite:
            for old, _ in clashes:
                del existing[old]
        elif clashes:
            raise ValueError("There are already Waypoints with those "
                             "times in this timeline:\n"
                             f"{clashes}")

        self.parent.is_animated = True

        existing |= newcomers

        self.parent.tag.clear()

        for t, w in sorted(existing.items()):
            self.parent.tag.append(copy.copy(w.tag))

        return self

    def __getitem__(self, time):
        if 'x_y' in str(self.parent._tag):
            raise ValueError()
        for t, wt in self.parent._waypoints().items():
            if t==time:
                return wt
            elif t>time:
                raise KeyError(time)

        raise KeyError(time)

    def __setitem__(self, t, v):

        t = self._ensure_fps(t)

        if isinstance(v, Waypoint):
            new_waypoint = v
            new_waypoint.time = t
        elif isinstance(v, self.parent.__class__):
            new_waypoint = Waypoint(
                    time = t,
                    value = v,
                    )
        else:
            new_waypoint = Waypoint(
                    time = t,
                    value = self.parent.__class__(v),
                    )

        if not self.parent.is_animated:
            self.parent._tag.clear()
            self.parent._set_animated(
                    whether = True,
                    adjust_contents = False,
                    )

        waypoints = self.parent._waypoints()

        waypoints[t] = new_waypoint

        self.parent._set_waypoints(waypoints.values())

    def __delitem__(self, t):

        if isinstance(t, (int, float, str)):
            t = T(t, ref = self.parent._tag)
        elif isinstance(t, T):
            t = self._ensure_fps(t)

        waypoints = self.parent._waypoints()

        waypoints.__delitem__(t)

        self.parent._set_waypoints(waypoints.values())

    def __eq__(self, other):
        if isinstance(other, Timeline):
            return self.values()==other.values()
        else:
            return self.values()==list(other)

    def __str__(self):
        result = (
                f'[timeline of {self.parent.__class__.__name__}:'
                f'{self.parent._waypoints()}]'
                )
        return result

    def __len__(self):
        return len(self.keys())

    def __bool__(self):
        return len(self)!=0

    __repr__ = __str__

#######################

INTERPOLATION_TYPES = {
        # UI name    XML name   emoji
        'tcb':      ('auto',     '🟢'),
        'clamped':  ('clamped',  '🔶'),
        'constant': ('constant', '🟥'),
        'linear':   ('linear',   '🌽'), # yeah, I know it's sweetcorn
        'ease':     ('halt',     '🫐'), # blueberry
        'undefined': (None,      '🪨'), # rock
        }

INTERPOLATION_TYPE_SYNONYMS = dict(
        [(v[0], k)
         for k,v in INTERPOLATION_TYPES.items()
         if v[0] is not None])

INTERPOLATION_TYPES_INVERSE = dict(
        [(xml, ui)
         for ui, (xml, emoji) in INTERPOLATION_TYPES.items()
         if xml is not None
         ])

@functools.total_ordering
class Waypoint:
    """
    A waypoint is a marker on a layer field's timeline,
    recording that the attribute should have the given value at the
    given time. It also gives the interpolation, before and after:
    that is, the behaviour of the value between this waypoint and
    those on either side.

    `Waypoint`s can be compared with other `Waypoint`s: earlier times
    sort before later times.

    Arguments:
        value: the value of the attribute at the given time.
            Must not be animated: can you imagine a timeline
            where there were animations inside the animations?
            Enough to give anyone a headache and a `ValueError`.
        time: when the attribute should reach this value.
            On reading, this is always `T`. It can also be set using
            a string or an integer; in these cases it is cast to `T`
            on reading; where `T` would require a reference tag,
            the waypoint's own tag is used. For any other type,
            raises `TypeError`.
        after: one of the interpolation behaviours.
            In string representations of Waypoints, each is represented
            by an emoji which (somewhat) corresponds to the symbol used
            by Synfig Studio. They are:

            - `tcb` (🟢)
            - `clamped` (🔶) (the default)
            - `constant` (🟥)
            - `linear` (🌽)
            - `ease` (🫐)

            These are the names used in Synfig Studio's UI. You can also
            use the names that appear in .sif files; they are misleading,
            so this is probably better avoided. They are:

            - `auto` (synonym for `tcb`)
            - `halt` (synonym for `ease`)

            The other behaviours have the same names in both.

            Unknown names raise `TypeError`. If a `Waypoint` is found with
            interpolations which don't fit into our understanding,
            they appear as "undefined" (🪨). This shouldn't happen.
        before: see `after`.

    Raises:
        TypeError: if `before` or `after` isn't the name of an
            interpolation type.

    Attributes:
        tag (bs4.Tag): the tag which would represent this Waypoint
            in a .sif file.
    """

    def __init__(self,
                 time:T,
                 value: Any,
                 before: str='clamped',
                 after: str='clamped'):

        if not isinstance(value, Value):
            raise TypeError(value)

        if value.is_animated:
            raise ValueError("Waypoints can't have animated values")

        before = self._check_interpolation_type(before, True)
        after = self._check_interpolation_type(after, True)

        self.tag = bs4.Tag(name="waypoint")
        self.tag['time'] = str(time)
        self.tag['before'] = INTERPOLATION_TYPES[before][0]
        self.tag['after']  = INTERPOLATION_TYPES[after ][0]
        self.tag.append(
                copy.copy(
                    value.tag
                    )
                )

    @property
    def time(self) -> T:
        try:
            return T(self.tag['time'],
                     ref = self.tag,
                     )
        except ValueError:
            raise ValueError(
                    "If a tag isn't attached to a document, "
                    "its time value must be expressed in frames: "
                    f"{self.tag['time']}"
                    )

    @time.setter
    def time(self, value:Any):
        value = T(value, ref=self.tag)

        self.tag['time'] = str(value)

    @property
    def before(self) -> str:
        return INTERPOLATION_TYPES_INVERSE[self.tag['before']]

    @before.setter
    def before(self, v:str):
        v = self._check_interpolation_type(v, False)
        self.tag['before'] = v

    @property
    def after(self) -> str:
        return INTERPOLATION_TYPES_INVERSE[self.tag['after']]

    @after.setter
    def after(self, v:str):
        v = self._check_interpolation_type(v, False)
        self.tag['after'] = v

    @property
    def value(self) -> Value:
        value_tag = self._get_value_tag()

        return Value.from_tag(value_tag)

    @value.setter
    def value(self, v:Value):
        self._get_value_tag().extract()
        self.tag.append(v.tag)

    def _get_value_tag(self):
        for value_tag in self.tag.children:
            if isinstance(value_tag, bs4.Tag):
                return value_tag
        else:
            # shouldn't happen
            raise ValueError(f"tag has no value! {self.tag}")

    @classmethod
    def _check_interpolation_type(cls, v, from_constructor):

        if v=='undefined':
            if from_constructor:
                raise ValueError(
                        "Waypoints can't have interpolations "
                        "of 'undefined'."
                        )
            else:
                raise ValueError(
                        "You can't set waypoint interpolations "
                        "to 'undefined'."
                        )

        if v in INTERPOLATION_TYPES:
            return v

        if v in INTERPOLATION_TYPE_SYNONYMS:
            return INTERPOLATION_TYPE_SYNONYMS[v]

        raise ValueError(f"Unknown interpolation type: {v}")

    @classmethod
    def from_tag(cls,
                 tag: bs4.Tag,
                 our_type:(str|None) = None,
                 ):
        if tag.name!='waypoint':
            raise ValueError("Waypoints must be called <waypoint>: "
                                f"{tag}")


        # Don't validate the time here; we can check it when they ask
        # for it. They might be just about to put the new tag into an
        # animation, such that the time would then validate.

        v = [t for t in tag.children if isinstance(t, bs4.element.Tag)]

        if len(v)==0:
            raise ValueError(f"Waypoint without a value: {w}")
        elif len(v)!=1:
            raise ValueError(
                    f"Waypoint with multiple values: {w}")
        elif v[0].name==Value.ANIMATED:
            raise ValueError("Values in waypoints cannot themselves "
                             "be animated")
        elif our_type is not None and v[0].name!=our_type:
            raise ValueError(
                    "Waypoint type must match parent: "
                    f"parent={our_type}, child={v[0].name}")

        result = cls.__new__(cls)
        result.tag = tag

        return result

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        if not isinstance(other, Waypoint):
            return False

        return self.time == other.time

    def __str__(self):
        return '[%3s ' % (self.tag['time'],) + (
                f'{INTERPOLATION_TYPES[self.before][1]}-'
                f'{INTERPOLATION_TYPES[self.after][1]} - '
                f'{self.value}]'
                )

    __repr__ = __str__

__all__ = [
        'Value',
        'Timeline',
        'Waypoint',
        ]
