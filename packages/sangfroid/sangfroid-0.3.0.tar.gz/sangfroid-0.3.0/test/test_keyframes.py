from test import *
import sangfroid
from sangfroid import T

def test_keyframes_simple():
    sif = get_animation('circles.sif')

    assert len(sif.keyframes)==6

    for k, expected in zip(sif.keyframes, EXPECTED_CIRCLES_KEYFRAMES):
        assert (k.time.frames, k.name, k.active) == expected

def test_keyframes_str():
    sif = get_animation('circles.sif')

    assert str(sif.keyframes)==EXPECTED_CIRCLES_STR
    assert repr(sif.keyframes)==EXPECTED_CIRCLES_STR

EXPECTED_CIRCLES_KEYFRAMES = [
        (0, "it's white", True),
        (20, "now it's pink", True),
        (25, "now it's mauve", True),
        (33, 'this one is inactive', False),
        (35, 'blue', True),
        (41, '', True),
        ]

EXPECTED_CIRCLES_STR = """Keyframes of [📂animation 'I like circles. They are round.']:
  - 0f "it's white"
  - 20f "now it's pink"
  - 1s 1f "now it's mauve"
  - 1s 9f 'this one is inactive' (inactive)
  - 1s 11f 'blue'
  - 1s 17f ''"""
