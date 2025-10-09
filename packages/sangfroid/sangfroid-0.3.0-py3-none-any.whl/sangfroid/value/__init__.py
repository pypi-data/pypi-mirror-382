"""
Value objects represent the values of a layer's fields.

For example, you might be animating the second hand on a clock.
The Layer representing the second hand will have a Field called `"angle"`.
The Value of that field will be an angle, such as 45°.

Each type of Value has its own subclass: there's one for angles,
one for vectors, one for colours, and so on.

Values are either animated or not animated. If they are
animated, they have a Timeline holding different states
of the Value at different times.
"""

from sangfroid.value.value import *

from sangfroid.value.blendmethod import *
from sangfroid.value.canvas import *
from sangfroid.value.color import *
from sangfroid.value.vector import *
from sangfroid.value.gradient import *
from sangfroid.value.simple import *
from sangfroid.value.string import *
from sangfroid.value.tbd import *
from sangfroid.value.transformation import *

__all__ = [
        cls.__name__.title()
        for cls in Value.handles_type.handlers.values()
        ]
