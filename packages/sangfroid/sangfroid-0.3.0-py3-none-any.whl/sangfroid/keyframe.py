"""
named instants on a timeline
"""
from sangfroid.t import T
from typing import List

class Keyframe:
    """
    A *named* instant on an animation's timeline. For example,
    a keyframe could represent an event happening two seconds
    into the animation.

    Attributes:
        active (bool): whether the keyframe is enabled.
            Doesn't affect Sangfroid, but Synfig will ignore
            keyframes which have `active` set to `False`.
        time (T): the time of this keyframe.
        name (str): the name of this keyframe.
    """
    def __init__(self, tag):
        self._tag = tag

    @property
    def time(self):
        return T(self._tag['time'],
                 ref = self._tag,
                 )

    @property
    def name(self):
        return self._tag.text

    @property
    def active(self):
        if self._tag['active']=='true':
            return True
        else:
            return False

    def __str__(self):
        if self.active:
            active = ''
        else:
            active = ' (inactive)'
        return f'{self.time} {repr(self.name)}{active}'

    __repr__ = __str__

    @classmethod
    def all_in_animation(cls, animation) -> List:
        """
        Returns all the keyframes in an animation.

        Arguments:
            animation (Animation): the animation we're looking at
        """
        result = Keyframes.__new__(Keyframes)
        result.animation = animation

        return result

class Keyframes:
    """
    All the keyframes in an animation.

    This is iterable. You can't instantiate it; you should
    get hold of it by calling the `all_in_animation`
    class method of `Keyframe`.
    """
    def __init__(self):
        raise ValueError("Don't instantiate the Keyframes class directly.")

    def __len__(self):
        return len(self.animation.tag.find_all('keyframe'))

    def __iter__(self):
        for keyframe_tag in self.animation.tag.find_all('keyframe'):
            yield Keyframe(keyframe_tag)

    def __str__(self):
        result = f'Keyframes of {self.animation}:'
        if len(self)==0:
            result += '\n  (none)'
        else:
            for keyframe in self:
                result += f'\n  - {keyframe}'

        return result

    __repr__ = __str__

__all__ = [
        'Keyframe',
        ]
