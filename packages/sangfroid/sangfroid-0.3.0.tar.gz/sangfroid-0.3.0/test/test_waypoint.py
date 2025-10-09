import sangfroid
from sangfroid.value.value import Waypoint
from sangfroid.value import Real, Angle
from sangfroid.t import T
from test import *
import bs4
import pytest

def test_waypoint_loaded():
    sif = get_animation('bouncing.sif')

    ball = sif.find(desc='Ball')
    angle = ball['transformation']['angle']

    assert not angle.is_animated
    assert angle.timeline==[]
    assert not angle.timeline
    assert len(angle.timeline)==0

    scale = ball['transformation']['scale']

    assert scale.is_animated
    assert scale.timeline!=[]
    assert scale.timeline
    assert len(scale.timeline)==3

    for found, expected in zip(scale.timeline.values(), [
        ( '0f', 'ease', 'ease'),
        ('24f', 'linear', 'linear'),
        ('48f', 'ease', 'ease'),
        ]):

        assert found.time==T(expected[0])
        assert found.before==expected[1]
        assert found.after==expected[2]

def test_value_set_is_animated():
    sif = get_animation('bouncing.sif')
    
    ball = sif.find(desc='Ball')
    angle = ball['transformation']['angle']

    assert not angle.is_animated
    angle.is_animated = True
    assert angle.is_animated
    angle.timeline[T('1s')] = Angle(90)

    angle.is_animated = False
    assert not angle.is_animated

def test_waypoint_interpolation_types():

    value = sangfroid.value.Bool(True)

    for source_type, expected_type, expected_emoji in [
            ('auto',     'tcb',      '🟢'),
            ('tcb',      'tcb',      '🟢'),
            ('clamped',  'clamped',  '🔶'),
            ('constant', 'constant', '🟥'),
            ('linear',   'linear',   '🌽'),
            ('ease',     'ease',     '🫐'),
            ('halt',     'ease',     '🫐'),
            ]:
        waypoint = Waypoint(T('0f'), value=value,
                            before=source_type, after=source_type)

        assert waypoint.before == expected_type, source_type
        assert waypoint.after  == expected_type, source_type

        found_emoji = str(waypoint).split(' ')[2]
        assert found_emoji == f'{expected_emoji}-{expected_emoji}'

    with pytest.raises(ValueError):
        Waypoint(time=T('0f'), value=value, before='undefined', after='auto')

    with pytest.raises(ValueError):
        Waypoint(time=T('0f'), value=value, before='wombat', after='auto')

def test_waypoint_silly():

    value = sangfroid.value.Bool(True)

    with pytest.raises(ValueError):
        # silly interpolation type
        Waypoint(time=T('0f'), value=value, before='wombat', after='ease')

    with pytest.raises(TypeError):
        # values must be sangfroid.value.Values
        Waypoint(time=T('0f'), value=True)

def test_waypoint_time_spec():
    value = sangfroid.value.Bool(True)
    w1 = Waypoint(time=T('20f'), value=value).time
    assert int(w1)==20

    with pytest.raises(ValueError):
        Waypoint(time='bananas', value=value).time

    with pytest.raises(ValueError):
        Waypoint(time=None, value=value).time

def test_waypoint_set_time_attr():
    sif = get_animation('bouncing.sif')
    value = sangfroid.value.Bool(True)

    waypoint = Waypoint(
            time=T('20f'),
            value = value,
            )
    assert int(waypoint.time)==20

    waypoint.time = 30
    assert int(waypoint.time)==30

    waypoint.time = T(40)
    assert int(waypoint.time)==40

    waypoint.time = T('50f')
    assert int(waypoint.time)==50

    with pytest.raises(ValueError):
        waypoint.time = {'not', 'a', 'valid', 'time'}

    with pytest.raises(ValueError):
        waypoint.time = '10s'

def test_waypoint_value_spec():
    sif = get_animation('bouncing.sif')

    value = sangfroid.value.Bool(True)
    w1 = Waypoint(time=T('20f'), value=value)
    assert int(w1.time)==20
    assert w1.value==True
    assert str(w1)=='[20f 🔶-🔶 - True]'

    with pytest.raises(TypeError):
        w2 = Waypoint(time=T('40f'), value=False)

    sif = get_animation('bouncing.sif')
    shadow = sif.find(desc='Shadow circle')
    invert = shadow['invert']

    assert not invert.is_animated
    invert.is_animated = True
    del invert.timeline[0]
    invert.timeline[10] = w1
    invert.timeline[20] = False

    assert len(invert.timeline)==2

    assert (
            [str(n) for n in invert.timeline.items()]==
            [
                '(10f, [10f 🔶-🔶 - True])',
                '(20f, [20f 🔶-🔶 - False])',
                ]
            )

def test_waypoint_del():
    sif = get_animation('bouncing.sif')
    assert sif.framecount==121

    ball = sif.find(desc='Bouncy ball')
    color = ball['color']
    assert not color.is_animated

    color.timeline[0] = '#FF0000'
    color.timeline[16] = '#00FF00'
    color.timeline[32] = '#0000FF'
    color.timeline[40] = '#FF00FF'
    color.timeline[47] = '#FF0000'

    def assert_timeline(values, reason):
        assert (
                [(t.frames,str(w.value)) for t,w in color.timeline.items()] ==
                values
                ), reason
        if values:
            assert color.is_animated
        else:
            assert not color.is_animated

    assert_timeline([
            (0.0, '#ff0000'),
            (16.0, '#00ff00'),
            (32.0, '#0000ff'),
            (40.0, '#ff00ff'),
            (47.0, '#ff0000'),
            ], "original is as expected")

    with pytest.raises(KeyError):
        del color.timeline[177]

    del color.timeline[32]

    assert_timeline([
            (0.0, '#ff0000'),
            (16.0, '#00ff00'),
            (40.0, '#ff00ff'),
            (47.0, '#ff0000'),
            ], "we can delete by int frames number")

    with pytest.raises(KeyError):
        # but not the same twice!
        del color.timeline[32]

    del color.timeline[40.0]

    assert_timeline([
            (0.0, '#ff0000'),
            (16.0, '#00ff00'),
            (47.0, '#ff0000'),
            ], "we can delete by float frames number")

    del color.timeline[T(16)]

    assert_timeline([
            (0.0, '#ff0000'),
            (47.0, '#ff0000'),
            ], "we can delete by T(int)") # colour by Tint, ha

    del color.timeline['1s23f']

    assert_timeline([
            (0.0, '#ff0000'),
            ], "we can delete by T(str)")

    del color.timeline[T(0)]

    assert_timeline([
        ], "we can delete until there's nothing left")

def test_waypoint_add():
    sif = get_animation('bouncing.sif')
    assert len(sif)==121

    ball = sif.find(desc='Bouncy ball')
    color = ball['color']
    assert not color.is_animated

    color.timeline[0] = '#FF0000'
    color.timeline[16] = '#00FF00'
    color.timeline[32] = '#0000FF'
    color.timeline[40] = '#FF00FF'
    color.timeline[47] = '#FF0000'

    def assert_timeline(values, reason):
        assert (
                [(t.frames,str(w.value)) for t,w in color.timeline.items()] ==
                values
                ), reason
        if values:
            assert color.is_animated
        else:
            assert not color.is_animated

    assert_timeline([
            (0.0, '#ff0000'),
            (16.0, '#00ff00'),
            (32.0, '#0000ff'),
            (40.0, '#ff00ff'),
            (47.0, '#ff0000'),
            ], "original is as expected")

    with pytest.raises(KeyError):
        del color.timeline[177]

    del color.timeline[32]

    assert_timeline([
            (0.0, '#ff0000'),
            (16.0, '#00ff00'),
            (40.0, '#ff00ff'),
            (47.0, '#ff0000'),
            ], "we can delete by int frames number")

    with pytest.raises(KeyError):
        # but not the same twice!
        del color.timeline[32]

    del color.timeline[40.0]

    assert_timeline([
            (0.0, '#ff0000'),
            (16.0, '#00ff00'),
            (47.0, '#ff0000'),
            ], "we can delete by float frames number")

    del color.timeline[T(16)]

    assert_timeline([
            (0.0, '#ff0000'),
            (47.0, '#ff0000'),
            ], "we can delete by T(int)") # colour by Tint, ha

    del color.timeline['1s23f']

    assert_timeline([
            (0.0, '#ff0000'),
            ], "we can delete by T(str)")

    del color.timeline[T(0)]

    assert_timeline([
        ], "we can delete until there's nothing left")

def test_waypoint_add():
    sif = get_animation('bouncing.sif')

    ball = sif.find(desc='Bouncy ball')
    color = ball['color']
    assert not color.is_animated

    color.timeline[0] = '#FF0000'
    color.timeline[16] = '#00FF00'
    color.timeline[32] = '#0000FF'
    color.timeline[47] = '#FF0000'

    waypoint_details = [str(c) for c in color.tag.children
                        if isinstance(c, bs4.Tag)]

    assert waypoint_details == [
            ('<waypoint after="clamped" before="clamped" time="0f"><color>'
             '<r>1.000000</r><g>0.000000</g><b>0.000000</b><a>1.000000</a>'
             '</color></waypoint>'),
            ('<waypoint after="clamped" before="clamped" time="16f"><color>'
             '<r>0.000000</r><g>1.000000</g><b>0.000000</b><a>1.000000</a>'
             '</color></waypoint>'),
            ('<waypoint after="clamped" before="clamped" time="1s 8f"><color>'
             '<r>0.000000</r><g>0.000000</g><b>1.000000</b><a>1.000000</a>'
             '</color></waypoint>'),
            ('<waypoint after="clamped" before="clamped" time="1s 23f"><color>'
             '<r>1.000000</r><g>0.000000</g><b>0.000000</b><a>1.000000</a>'
             '</color></waypoint>'),
            ]

def test_value_timeline_add():
    def get_example_value():
        sif = get_animation('bouncing.sif')

        ball = sif.find(desc='Bouncy ball')
        amount = ball['amount']
        amount.timeline[0] = 7
        return amount

    def timeline_details(v):
        return [(w.time.seconds, float(w.value)) for w in v.timeline]

    v = get_example_value()
    assert timeline_details(v)==[(0.0, 7.0)]

def test_value_timeline_assign_once():
    r = Real(1.77)
    assert str(r)=='1.77'

    r.timeline = [
            Waypoint(time=T('0f'), value=Real(1.0)),
            Waypoint(time=T('1f'), value=Real(2.0)),
            ]

    s = Real(1.77)
    s.timeline = r.timeline

    for obj in [r, s]:
        assert [str(w.value) for w in obj.timeline] == ['1.0', '2.0']

    assert r.timeline[0] == s.timeline[0]
    assert r.timeline[0] is not s.timeline[0]

def test_value_timeline_assign_twice():
    r = Real(1.77)
    assert str(r)=='1.77'
    assert r.is_animated == False

    r.timeline = [
            Waypoint(time=T('0f'), value=Real(1.0)),
            ]
    assert r.is_animated == True
    assert len(r.timeline)==1
    assert r.timeline[0].time == T('0f')
    with pytest.raises(KeyError):
        r.timeline[1]

    r.timeline = [
            Waypoint(time=T('1f'), value=Real(2.0)),
            ]
    assert r.is_animated == True
    assert len(r.timeline)==1
    with pytest.raises(KeyError):
        r.timeline[0]
    assert r.timeline[1].time == T('1f')

def test_value_get_is_animated():
    sif = get_animation('bouncing.sif')

    ball = sif.find(desc='Ball')
    scale = ball['transformation']['scale']

    assert scale.is_animated
    original_point_0 = str(scale.timeline[0].value)

    scale.is_animated = False
    assert not scale.is_animated
    assert str(scale)==original_point_0

    scale.is_animated = True
    assert scale.is_animated

    assert str(scale.timeline[0].value)==original_point_0

def test_value_set_is_animated():
    sif = get_animation('bouncing.sif')

    ball = sif.find(desc='Ball')
    angle = ball['transformation']['angle']

    assert not angle.is_animated
    angle.is_animated = True
    assert angle.is_animated
    angle.timeline['1s'] = 90

    angle.is_animated = False
    assert not angle.is_animated

def test_waypoint_overwrite_or_not():

    def via_iadd(timeline, values):
        timeline += values

    def via_add_with_overwrite(timeline, values):
        timeline.add(values, overwrite=True)

    def via_add_with_no_overwrite(timeline, values):
        timeline.add(values, overwrite=False)

    def waypoint(t, v):
        return Waypoint(t, Angle(v))

    for method, can_overwrite in [
            (via_iadd, True),
            (via_add_with_overwrite, True),
            (via_add_with_no_overwrite, False),
            ]:

        sif = get_animation('bouncing.sif')

        ball = sif.find(desc='Ball')
        angle = ball['transformation']['angle']

        def assert_timeline_is_like(expected):
            found = [
                    (w.time.frames, float(w.value))
                    for w in angle.timeline
                    ]
            assert found==expected, method

        assert not angle.is_animated
        assert_timeline_is_like([])

        with pytest.raises(TypeError):
            method(angle.timeline, 100)

        with pytest.raises(TypeError):
            method(angle.timeline, [100, 200])

        method(angle.timeline,
               waypoint(10, 10.0))

        assert_timeline_is_like([
            (10, 10.0),
            ])

        method(angle.timeline,
               waypoint(20, 20.0))

        assert_timeline_is_like([
            (10, 10.0),
            (20, 20.0),
            ])

        method(angle.timeline, [
            waypoint(30, 30.0),
            waypoint(40, 40.0),
            ])

        assert_timeline_is_like([
            (10, 10.0),
            (20, 20.0),
            (30, 30.0),
            (40, 40.0),
            ])

        try:
            method(angle.timeline, [
                waypoint(40, 45.0),
                waypoint(50, 50.0),
                ])

            it_worked = True
        except ValueError:
            it_worked = False

        assert it_worked==can_overwrite, method

        if it_worked:
            assert_timeline_is_like([
                (10, 10.0),
                (20, 20.0),
                (30, 30.0),
                (40, 45.0),
                (50, 50.0),
                ])
        else:
            assert_timeline_is_like([
                (10, 10.0),
                (20, 20.0),
                (30, 30.0),
                (40, 40.0),
                ])

def test_waypoint_interpolation_name_in_svg():
    value = sangfroid.value.Bool(True)

    for name, expected in [
            ('tcb',   'auto'),
            ('auto',  'auto'),
            ('clamped', 'clamped'),
            ('constant', 'constant'),
            ('linear', 'linear'),
            ('ease', 'halt'),
            ('halt', 'halt'),
            ]:

        waypoint = Waypoint(T('0f'),
                            value=value,
                            before=name,
                            after=name,
                            )
        tag = waypoint.tag

        assert tag['before'] == expected, name
        assert tag['after' ] == expected, name

def test_timeline_gives_ref_to_waypoints():
    sif = get_animation('bouncing.sif')
    timeline = sif.find(desc='Ball').offset.timeline

    first = timeline[0]

    first.time = '10s' # which would fail with no ref
