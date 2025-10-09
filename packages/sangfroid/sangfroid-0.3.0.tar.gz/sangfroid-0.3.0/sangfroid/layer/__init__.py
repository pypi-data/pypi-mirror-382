"""
Many kinds of layer.

The topmost kind of layer in an animation will
always be an instance of `sangfroid.Animation`.
But layers inside that will be instances of one of
these classes.
"""

from sangfroid.layer.layer import *

from sangfroid.layer.blurs import *
from sangfroid.field import *
from sangfroid.layer.geometry import *
from sangfroid.layer.group import *
from sangfroid.layer.other import *
from sangfroid.layer.stylise import *
from sangfroid.layer.text import *
from sangfroid.layer.time import *
from sangfroid.layer.tbd import *
from sangfroid.layer.transform import *

__all__ = [
        cls.__name__.title()
        for cls in Layer.handles_type.handlers.values()
        ]
