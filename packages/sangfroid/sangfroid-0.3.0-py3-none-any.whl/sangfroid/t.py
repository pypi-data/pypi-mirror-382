"""
a type for timekeeping
"""
import math
import functools
import re
import bs4

@functools.total_ordering
class T:
    """
    An instant during an animation.

    This can be expressed either as a number of frames or as a number
    of seconds, both measured from the start of the animation.
    In both cases, it's a float, usually but not always integral.

    `T`s compare numerically to other `T`s, but they must have the
    same film speed unless the frame number is zero.

    `T` is immutable and hashable.

    If you cast a `T` to a string, and the film speed is unknown, it
    will always be a number of frames, like this: `89356f`. If the
    speed is known, you will get the time in hours, minutes,
    seconds, and frames, like this: `1h 2m 3s 4f`.

    Regret:
        This is unfortunate, since the constructor only accepts strings
        giving seconds and frames, not hours or minutes. Known issue;
        will fix.

    # The first parameter: the time

    This may be specified in one of four ways, where `F` represents
    any decimal integer or float:

    - an `int` or `float`, giving the number of frames counting forwards
          from the start of the animation. But if the number is negative,
          it counts backwards from the end, in the usual Python indexing style.

    - `"Ff"`

    - `"Fs"`

    - `"Fs Ff"`, in which case the values are added together.

    The number of seconds in the `"Fs"` or `"Fs Ff"` parameters may be negative,
    which allows you to set times before the start of the animation.
    However, the number of *frames* in a `"Fs Ff"` specification
    may not be negative.

    In time specifications giving both seconds and frames, the number
    of frames may be equal to or higher than the FPS. (So, for example,
    `"2s 48f"` is a valid time even if `fps=24`, when it's equivalent
    to `"4s`"`.)

    # The optional `ref` parameter

    When we're doing calculations with animated time, we often need
    to look up other things about the animation. The `ref` parameter
    points to the animation to consult.

    You may supply the root Beautiful Soup
    tag of an animation, or any of that tag's descendants. You may also
    supply a Sangfroid layer (or indeed any other object with a field "`tag`"),
    and its tag will be used.

    `ref` can also be `None`, or left unspecified. But there are two reasons
    you might *need* to specify a ref:

    - If an `int` or `float` specification is negative, so that it's
      relative to the end of the file. This is because we will need to
      look up the animation length.

    - If the specification is given as `"Fs"` or `"Fs Ff"`;
      this is because we need to look up the speed in frames per second.
      It's almost always 24. The reason we don't default to 24 is that
      it risks introducing subtle bugs which are only discovered when
      the actual frame rate isn't 24.

    In either case, if you don't specify a `ref`, we'll throw `ValueError`
    at the moment the lack of `ref` becomes a problem.

    However, if the time is zero (that is, at the start of the animation),
    the speed doesn't make a difference. So you may write the time as
    `"0s"` or `"0s 0f"` even if you don't supply a `ref`.

    But:
        That only works for the very common case of the time being zero.
        You can't write, say, `"0s 2f"` without supplying the `ref`, even
        though the film speed wouldn't make a difference, because that's
        a weird edge case. And that's where bugs come from.

    Attributes:
    """
    def __init__(
            self,
            value: (float|int|str) = 0.0,
            ref = None,
            ):
 
        if ref is None:
            root_tag = None
        elif isinstance(ref, bs4.Tag):
            root_tag = _canvas_root(ref)
        elif hasattr(ref, 'tag'):
            root_tag = _canvas_root(getattr(ref, 'tag'))
        else:
            raise TypeError(
                    "'ref' must be bs4.Tag, a Layer subclass, or None, "
                    f"but not {type(ref)}.")

        if root_tag is None:
            self._fps = None
        else:
            self._fps = float(root_tag['fps'])
        
            if self._fps<=0.0:
                raise ValueError(f"FPS must be positive: {self._fps}")

        try:
            if isinstance(value, str):
                self._frames = self._parse_time_spec(value)
            else:
                self._frames = float(value)

                if self._frames < 0:
                    if root_tag is None:
                        raise ValueError("Negative frame counts require "
                                         "an anchored ref.")

                    animation_duration = 1+(
                            self._parse_time_spec(
                                root_tag.attrs['end-time'],
                                )
                            - 
                            self._parse_time_spec(
                                root_tag.attrs['begin-time'],
                                )
                            )

                    self._frames = animation_duration + self._frames

        except TypeError:
            raise ValueError(f"Invalid time specification: {value}")

        assert isinstance(self._frames, float)

    def _parse_time_spec(self, s):
        assert isinstance(s, str)

        def complain(problem):
            raise ValueError(
                    f"bad time specification: {s}\n{problem}")

        s = s.strip()

        seconds = None
        frames = 0.0

        found = TIMESPEC_RE.split(s)
        if found is None:
            complain("This doesn't look like a time specification at all.")

        if len(found)==1:
            # a bare integer; make it into a number of frames
            found = [found[0]+'f']

        parts = {}
        for spec in found:
            if spec.strip()=='':
                continue
            elif spec[-1] in parts:
                complain(
                        f"The '{spec[-1]}' part was specified "
                        "more than once.")

            try:
                parts[spec[-1]] = float(spec[:-1])
            except ValueError:
                complain(
                        f"'{spec[:-1]}' is not a valid number.")

        seconds = None

        for unit, size in [
                ('h', 60*60),
                ('m', 60),
                ('s', 1),
                ]:
            if unit in parts:
                seconds = (seconds or 0.0) + parts[unit]*size

        result = 0.0

        if seconds is not None and seconds!=0.0:

            if self._fps is None:
                complain("Time specifications in seconds require "
                         "an anchored ref.")
            result += seconds * self._fps

        if 'f' in parts:
            if seconds and parts['f']<0:
                complain("If you give a number of seconds, the number "
                         "of frames can't be negative.")

            seconds = seconds or 0

            if seconds<0:
                result -= parts['f']
            else:
                result += parts['f']

        return result

    @property
    def frames(self) -> float:
        """
        Distance, in frames, from the start of the animation
        """
        return self._frames

    @property
    def fps(self) -> (float|None):
        """
        Speed of the film, if known, in frames per second.
        Always a positive float, or None if we don't know the speed.
        """
        return self._fps

    def __int__(self):
        return int(self._frames)

    def __float__(self):
        return self._frames

    @property
    def seconds(self) -> float:
        """
        Distance, in seconds, from the start of the animation.
        Raises `ValueError` if we don't know the film speed.
        """
        if self.fps is None:
            if self._frames==0.0:
                return 0.0
            else:
                raise ValueError(
                        "If you want to measure time in seconds, "
                        "you will need to specify the FPS.")
        return self._frames / self.fps

    def _compare(self, other, operator):

        if isinstance(other, self.__class__):
            if (
                    other.fps is not None and
                    self.fps is not None and
                    other.fps!=self.fps):
                raise ValueError(
                        "Comparison between two Ts with different FPS: "
                        f"{self}, {other}"
                        )

            other_f = other.frames
        elif isinstance(other, (float, int)):
            other_f = other
        else:
            return False

        return operator(self._frames, other_f)

    def __lt__(self, other):
        return self._compare(other, lambda a,b:a<b)

    def __eq__(self, other):
        return self._compare(other, lambda a,b:a==b)

    def __str__(self):
        if self._fps is None:
            return '%gf' % (self._frames, )

        frames = self._frames
        seconds = abs(self._frames/self._fps)

        result = []

        for unit, size in [
                ('h', 60*60),
                ('m', 60),
                ('s', 1),
                ]:

            if seconds>=size:
                result.append('%d%c' % (seconds//size, unit))
                seconds = seconds % size

        if seconds!=0 or result==[]:
            frames = abs(frames) % self._fps
            result.append('%gf' % (frames,))

        if self._frames<0:
            minus = '-'
        else:
            minus = ''

        result = minus + ' '.join(result)

        return result

    __repr__ = __str__

    def __hash__(self):
        if self._frames == 0:
            return 0

        s = (self._frames, self._fps)
        return hash(s)

# It doesn't matter that you can produce invalid decimals with this regex:
# that will be discovered when we do the float conversion.
TIMESPEC_RE = re.compile(
        r'(-?[0-9.]+[hmsf])'
        )

def _canvas_root(tag):
    parents = tag.find_parents()

    if len(parents)==0:
        return None
    elif len(parents)==1:
        root = tag
    else:
        root = parents[-2] # -1 is "document", the anon root tag

    if root.name=='canvas':
        return root
    else:
        return None

__all__ = [
        'T',
        ]
