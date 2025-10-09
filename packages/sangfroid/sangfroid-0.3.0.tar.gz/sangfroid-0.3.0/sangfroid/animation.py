"""
The outermost groups, representing the whole animation.
"""
from sangfroid.layer import (
        Group, Field, TagAttrField, NamedChildField,
        TagField,
        )
from sangfroid.format import Format, Blank
from sangfroid.keyframe import Keyframe
from sangfroid.value.color import Color
from sangfroid.t import T
import bs4
import sangfroid.value as v
from typing import List

class MetadataTagField(Field):
    pass

class TagTimeAttrField(TagAttrField):
    """
    An attribute on the main animation layer with a value of type T.
    """
    def __init__(self,
                 default,
                 **kwargs,
                 ):
        super().__init__(
                type_ = T,
                default = default,
                type_override = str,
                **kwargs,
                )

    def _get_value(self, obj, obj_type=None):
        s = super()._get_value(obj, obj_type)

        if s is None:
            return None

        return T(s,
                 ref = obj._tag,
                 )

class BgcolorField(TagAttrField):
    def __init__(self,
                 **kwargs,
                 ):
        super().__init__(
                type_ = T,
                default = '0.5 0.5 0.5 1.0',
                type_override = str,
                **kwargs,
                )

    def __get__(self, obj, obj_type=None):
        s = super().__get__(obj, obj_type)

        if s is None:
            return None

        return Color(*[float(n) for n in s.split(' ')])

    def __set__(self, obj, value):
        c = [('%0.06f' % (n/255)) for n in Color(value).as_tuple()]

        super().__set__(obj,
                        ' '.join(c)
                        )

class Animation(Group):
    """
    A Synfig animation. It can be loaded from a file in the
    `.sif`, `.sifz`, or `.sfg` formats.

    Note:
        `.sfg` support is currently broken. See
        [issue #2](https://gitlab.com/marnanel/sangfroid/-/issues/2).

    Synfig animations are made up of `[sangfroid.layer.Layer][]`s.
    Some of these layers, such as `Animation` itself, can contain other layers.
    `Animation` can only be the outermost layer, and it contains
    all the others. It also holds the list of keyframes,
    and some global settings, such as the frame speed and resolution.

    To load a file:
    ``` python
    import sangfroid

    sif = sangfroid.Animation('fred.sif')
    ```

    To start with a blank canvas:
    ``` python
    import sangfroid

    sif = sangfroid.Animation()
    ```
    """

    version = TagAttrField(float,       1.2)
    "The Synfig version which (notionally) created this animation"

    width = TagAttrField(int,         480)
    "The width of the canvas, in pixels."

    height = TagAttrField(int,         270)
    "The height of the canvas, in pixels."

    xres = TagAttrField(float,       2834.645669)
    "The horizontal resolution."

    yres = TagAttrField(float,       2834.645669)
    "The vertical resolution."

    gamma_r = TagAttrField(float,       1.0)
    gamma_g = TagAttrField(float,       1.0)
    gamma_b = TagAttrField(float,       1.0)
    view_box = TagAttrField(str, '-4.0 2.25 4.0 -2.25') # XXX wrong
    antialias = TagAttrField(int,         1) # XXX enum?

    fps = TagAttrField(float,       24.0)
    """The number of frames per second. Usually 24.

    (Can this be non-integer?)"""

    begin_time = TagTimeAttrField(0)
    """The time at which this animation starts.

    Almost always zero."""

    end_time = TagTimeAttrField('5s')
    "The time at which this animation ends."

    bgcolor = BgcolorField()

    background_first_color = MetadataTagField(v.Color, (0.88, 0.88, 0.88))
    background_rendering = MetadataTagField(v.Integer, 0)
    background_second_color = MetadataTagField(v.Color, (0.65, 0.65, 0.65))
    background_size = MetadataTagField(v.X_Y,     (15.0, 15.0))
    grid_color = MetadataTagField(v.Color, (0.623529, 0.623529, 0.623529))
    grid_show = MetadataTagField(v.Integer, 0)
    grid_size = MetadataTagField(v.X_Y, (0.25, 0.25))
    grid_snap = MetadataTagField(v.Integer, 0)
    guide_color = MetadataTagField(v.Color, (0.435294, 0.435294, 1.09))
    guide_show = MetadataTagField(v.Integer, 1)
    guide_snap = MetadataTagField(v.Integer, 0)
    jack_offset = MetadataTagField(v.Real, 0.0)
    onion_skin = MetadataTagField(v.Integer, 0)
    onion_skin_future = MetadataTagField(v.Integer, 0)
    onion_skin_keyframes = MetadataTagField(v.Integer, 1)
    onion_skin_past = MetadataTagField(v.Integer, 1)

    name = NamedChildField(str, 'Not yet named')
    """The name of this animation— not the filename,
    though it's often the same."""

    desc = NamedChildField(str, 'Animation')
    """
    A description of this animation, so you know what it is
    when you find it again next year.
    """

    canvas_tag = TagField()

    def __init__(self, filename:str|None=None):
        """
        Args:
            filename: the name of the main file to load.
                        If this is None, we create a blank animation.
        """
        self._filename = filename

        if filename is None:
            self._format = Blank()
        else:
            self._format = Format.from_filename(filename)

        with self._format.main_file() as soup:
            self._soup = soup

        assert len(self._soup.contents)==1
        tag = self._soup.contents[0]
        super().__init__(
                tag = tag,
                )

    @property
    def framecount(self) -> int:
        """
        The number of frames in this animation.

        Should be equal to `int(end_time)-int(begin_time)`.

        Note that this is one higher than the number of
        the last frame.
        """
        return int(T(-1, ref=self._tag).frames)+1

    @property
    def keyframes(self) -> List:
        """
        The defined keyframes.
        """
        return Keyframe.all_in_animation(self)
 
    def save(self, filename:str|None=None):
        """
        Saves the animation back out to disk.

        Args:
            filename: the filename to save the animation to.
                If None, we use the filename we loaded it from.
        """

        if filename is None:
            if self._format is None:
                raise ValueError(
                        "If you didn't give a filename at creation, "
                        "you must give one when you save."
                        )
            filename = self._format.filename
        else:
            new_format = Format.from_filename(filename,
                                              load = False,
                                              )
            if new_format!=self._format:
                # XXX copy the images over
                self._format = new_format

        self._format.save(
                content = self._soup,
                filename = filename,
                )

__all__ = [
        'Animation',
        ]
