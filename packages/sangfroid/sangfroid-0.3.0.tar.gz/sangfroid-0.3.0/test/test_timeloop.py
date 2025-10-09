from test import *
import sangfroid

def test_timeloop_time_param_name():
    tl = sangfroid.layer.Timeloop()
    assert '_timebutstring' not in str(tl._tag)
