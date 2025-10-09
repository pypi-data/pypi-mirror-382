"""
handle Synfig animations

Sangfroid allows you to load, change, and save Synfig animations
using Python.
"""
import sangfroid.layer
import sangfroid.value
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mkdocs-api-autonav")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "uninstalled"

__author__ = "Marnanel Thurman"
__email__ = "marnanel@marnanel.org"

from sangfroid.keyframe import *
from sangfroid.animation import *
from sangfroid.t import *

def open(filename:str) -> sangfroid.Animation:
    """
    Loads the Synfig file with the given filename.

    Args:
        filename: the name of the source file. Can be .sfg, .sif,
            or .sifz.
    """
    result = Animation(filename)
    return result

__all__ = [
        'layer',
        'Canvas',
        'Keyframe',
        'Animation',
        'T',

        'open',
        ]
