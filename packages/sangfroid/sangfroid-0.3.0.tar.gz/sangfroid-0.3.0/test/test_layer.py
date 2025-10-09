import re
import sangfroid
import pytest
import os
from test import *

def test_layer_children():
    sif = get_animation('pick-and-mix.sif')

    found = [re.search(r'([a-z]+)', str(layer))[0]
             for layer in sif.descendants]

    assert found==[
            "zoom",
            "translate",
            "rotate",
            "timeloop",
            "stroboscope",
            "freetime",
            "shade",
            "bevel",
            "xor",
            "text",
            "switch",
            "super",
            "sound",
            "skeleton",
            "plant",
            "switch",
            "group",
            "filter",
            "duplicate",
            "spiral",
            "radial",
            "noise",
            "linear",
            "curve",
            "conical",
            "star",
            "solid",
            "region",
            "rectangle",
            "polygon",
            "outline",
            "outline",
            "circle",
            "checker",
            "advanced",
            "mandelbrot",
            "julia",
            "lumakey",
            "halftone",
            "halftone",
            "colorcorrect",
            "clamp",
            "chromakey",
            "simple",
            "metaballs",
            "warp",
            "twirl",
            "stretch",
            "spherize",
            "skeleton",
            "noise",
            "inside",
            "curve",
            "radial",
            "motion",
            "blur",
            ]

def test_layer_items(dump = False):
    sif = get_animation('bouncing.sif')

    def format_value(v):
        result = f'{v.__class__.__name__}, {v}'
        if v.is_animated:
            result += ', animated'
        return result

    found = ''
    for layer in sif.descendants:
        found += f'{layer}\n'

        for k, v in layer.items():

            if isinstance(v, sangfroid.value.Composite):
                found += f' - {k}:\n'
                for k2, v2 in v.items():
                    found += f'     - {k2} = '+format_value(v2)+'\n'
            else:
                found += f' - {k}: '+format_value(v)+'\n'

    if dump:
        print(found)
    else:
        assert found == LAYER_ITEMS_EXPECTED

def test_layer_items_doesnt_pick_up_subparams():
    sif = sangfroid.Animation()

    assert len(sif.items())==0

    sif.append(sangfroid.layer.Text())

    assert len(sif.items())==0

def _find_type_names_of_children_of_layer(layer):
    """
    Given a layer, returns a list of strings, each being the name of a
    layer which is a child of the parameter, in order; if a layer has
    no name, the member is None. The result is in the same order that
    the layers appear in the sif file.

    This gives a sort of signature for checking that the layers we find
    are the layers we expected to find.
    """
    result = [
            [
            b.type_
            for b in a
            ] for a in layers
            ]
    return result

def _find_the_shadows(t):
    return 'shadow' in t.get('desc', '').lower()

def test_layer_find_all_simple():
    sif = get_animation('bouncing.sif')
    shadows = sif.find_all(desc='Shadow')
    assert [x.desc for x in shadows] == ['Shadow', 'Shadow']

    circles = sif.find_all('circle')
    assert [x.desc for x in circles] == [
            'Shadow circle', 'Bouncy ball']

    wombats = list(sif.find_all('wombat'))
    assert wombats == []

    everything = list(sif.find_all(True))
    assert len(everything)==11

    shadows = [x.desc for x in sif.find_all(_find_the_shadows)]
    assert sorted(shadows)==['Shadow', 'Shadow', 'Shadow circle']

    bananas = sif.find_all(desc='Banana')
    assert len(bananas)==0

def test_layer_find_all_recursive():
    sif = get_animation('bouncing.sif')

    shadows = [x.desc for x in sif.find_all(_find_the_shadows,
                                            recursive=False,
                                            )]
    assert sorted(shadows)==['Shadow']

    shadows = [x.desc for x in sif.find_all(_find_the_shadows,
                                            recursive=True,
                                            )]
    assert sorted(shadows)==['Shadow', 'Shadow', 'Shadow circle']

def test_layer_find():
    sif = get_animation('circles.sif')
    orange_circle = sif.find(desc='Orange circle')
    assert isinstance(orange_circle, sangfroid.layer.Layer)
    assert orange_circle.desc == 'Orange circle'

    pink_circle = sif.find(desc='Pink circle')
    assert pink_circle is None, 'Matching nothing gives None'

def test_layer_item_get():
    sif = get_animation('circles.sif')
    green_circle = sif.find(desc='Green circle')
    logger.debug("dir(%s) == %s", green_circle, dir(green_circle))
    assert green_circle.radius == 0.5055338531

    try:
        green_circle.wombat
        ok = False
    except AttributeError:
        ok = True

    assert ok, 'use of unreal attribute should raise KeyError'

def test_layer_item_set():
    sif = get_animation('circles.sif')
    green_circle = sif.find(desc='Green circle')
    assert green_circle.color == '#10FF00', (
            'we can read the colour'
            )

    red = sangfroid.value.Color('#770000')
    green_circle.color = red
    assert green_circle.color == '#770000', (
            'colour has been set to red via Color'
            )

    green_circle.color = '#FFFF00'
    assert green_circle.color == '#FFFF00', (
            'colour has been set to yellow via string'
            )

    with pytest.raises(ValueError):
        green_circle.color = '2s'

    with pytest.raises(TypeError):
        green_circle.color = sangfroid.T(s=2)

def test_layer_item_contains():
    sif = get_animation('circles.sif')
    green_circle = sif.find(desc='Green circle')

    assert 'color' in green_circle
    assert 'wombat' not in green_circle

def test_layer_find_type():

    def names_of(n):
        return set([x.desc for x in n])

    sif = get_animation('circles.sif')

    circles = sif.find_all(type='circle')
    assert names_of(circles) == CIRCLES

    circles = sif.find_all(type=sangfroid.layer.Circle)
    assert names_of(circles) == CIRCLES

    circles = sif.find_all(type='CIRCLE')
    assert names_of(circles) == CIRCLES

    circles = sif.find_all(type='c_i_rcle')
    assert names_of(circles) == CIRCLES

def test_text_simple():
    sif = get_animation('pick-and-mix.sif')

    text = sif.find('text')
    assert text.text=='Hello wombat!'
    assert isinstance(text.text, sangfroid.value.String)

    text.text='Bananas'

    assert text.text=='Bananas'
    assert isinstance(text.text, sangfroid.value.String)

def test_text_from_string():

    text = sangfroid.layer.Text('This is a wombat')
    assert text.text=='This is a wombat'
    assert repr(text)=="[𝕋text 'This is a wombat']"

def test_layer_active():
    sif = get_animation('circles.sif')

    black = sif.find(desc='Black circle')
    assert black.active
    assert black.tag['active']=='true'

    black.active = False
    assert not black.active
    assert black.tag['active']=='false'

    black.active = True
    assert black.active
    assert black.tag['active']=='true'

    black.active = True
    assert black.active
    assert black.tag['active']=='true'

def test_layer_new():
    circle = sangfroid.layer.Circle()
    xml_compare(circle._tag, BLANK_CIRCLE,
                "Empty circle tag contains all it's supposed to")

def test_layer_subclasses_instantiate():

    cannot_instantiate = {}

    for subclass in sangfroid.layer.Layer.__subclasses__():
        in_module = subclass.__module__

        if in_module.startswith('test.'):
            continue
        elif in_module.endswith('.tbd'):
            continue

        try:
            subclass()
        except Exception as e:
            if int(os.environ.get('TEST_SUBCLASS_RAISES', 0))==1:
                raise
            else:
                cannot_instantiate[subclass.__name__]=str(e)

    def the_broken_ones():
        return '\n'.join([f'%20s - %s\n' % n
                          for n in cannot_instantiate.items()])

    assert len(cannot_instantiate)==0, (
        "All kinds of Layer can be instantiated"
        f"\n\n{the_broken_ones()}\n"
        "Set TEST_SUBCLASS_RAISES to 1 to raise an exception for\n"
        "each subclass as it breaks, or 0 (the default) for a\n"
        "summary of all of them."
        )

def test_layer_desc():

    STANDARD_GROUP_ATTR_TAGS = {
            'active': 'true',
            'exclude_from_rendering': 'false',
            'type': 'group',
            'version': sangfroid.layer.Group.SYNFIG_VERSION,
            }

    g = sangfroid.layer.Group()
    assert g._tag.attrs == STANDARD_GROUP_ATTR_TAGS

    g.desc = 'This is a group'
    assert g._tag.attrs == STANDARD_GROUP_ATTR_TAGS | {
            'desc': 'This is a group',
            }

    g.desc = ''
    assert g._tag.attrs == STANDARD_GROUP_ATTR_TAGS | {
            'desc': '',
            }

    g.desc = None
    assert g._tag.attrs == STANDARD_GROUP_ATTR_TAGS

LAYER_ITEMS_EXPECTED = """
[🕰️timeloop]
 - z_depth: Real, 0.0
 - link_time: Time, 0f
 - local_time: Time, 0f
 - duration: Time, 2s
 - only_for_positive_duration: Bool, False
 - symmetrical: Bool, True
[📂group 'Ball']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - origin: X_Y, (0.0, 0.0)
 - transformation:
     - offset = X_Y, (animated), animated
     - angle = Angle, 0°
     - skew_angle = Angle, 0°
     - scale = X_Y, (animated), animated
 - canvas: Canvas, [[-🔵circle 'Bouncy ball'], [-🫴bevel]]
 - time_dilation: Real, 1.0
 - time_offset: Time, 0f
 - children_lock: Bool, False
 - outline_grow: Real, 0.0
 - z_range: Bool, False
 - z_range_position: Real, 0.0
 - z_range_depth: Real, 0.0
 - z_range_blur: Real, 0.0
[-🫴bevel]
 - z_depth: Real, 0.0
 - amount: Real, 0.75
 - blend_method: Integer, 13
 - type: Integer, 1
 - color1: Color, #ffffff
 - color2: Color, #000000
 - angle: Angle, 89.0588°
 - depth: Real, 0.5819661441
 - softness: Real, 0.3276240462
 - use_luma: Bool, False
 - solid: Bool, False
 - fake_origin: X_Y, (0.0, 0.0)
[-🔵circle 'Bouncy ball']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - color: Color, #ff0000
 - radius: Real, 1.0
 - feather: Real, 0.0
 - origin: X_Y, (0.0, 0.0)
 - invert: Bool, False
[📂group 'Shadow']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - origin: X_Y, (-0.1150391698, -2.2065103054)
 - transformation:
     - offset = X_Y, (-0.1150391698, -2.2065103054)
     - angle = Angle, 0°
     - skew_angle = Angle, 0°
     - scale = X_Y, (animated), animated
 - canvas: Canvas, [[-📂group 'Shadow']]
 - time_dilation: Real, 1.0
 - time_offset: Time, 0f
 - children_lock: Bool, False
 - outline_grow: Real, 0.0
 - z_range: Bool, False
 - z_range_position: Real, 0.0
 - z_range_depth: Real, 0.0
 - z_range_blur: Real, 0.0
[-📂group 'Shadow']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - origin: X_Y, (0.0, 0.0)
 - transformation:
     - offset = X_Y, (0.0, -1.6003249884)
     - angle = Angle, 0°
     - skew_angle = Angle, 0°
     - scale = X_Y, (1.0, 0.3899480104)
 - canvas: Canvas, [[--🔵circle 'Shadow circle'], [--🟠blur]]
 - time_dilation: Real, 1.0
 - time_offset: Time, 0f
 - children_lock: Bool, False
 - outline_grow: Real, 0.0
 - z_range: Bool, False
 - z_range_position: Real, 0.0
 - z_range_depth: Real, 0.0
 - z_range_blur: Real, 0.0
[📂group 'Background']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - origin: X_Y, (0.0, 0.0)
 - transformation:
     - offset = X_Y, (0.0, 0.0)
     - angle = Angle, 0°
     - skew_angle = Angle, 0°
     - scale = X_Y, (1.0, 1.0)
 - canvas: Canvas, [[-▊solid_color 'wall'], [-🟦rectangle 'floor']]
 - time_dilation: Real, 1.0
 - time_offset: Time, 0f
 - children_lock: Bool, False
 - outline_grow: Real, 0.0
 - z_range: Bool, False
 - z_range_position: Real, 0.0
 - z_range_depth: Real, 0.0
 - z_range_blur: Real, 0.0
[-🟦rectangle 'floor']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - color: Color, #ffb356
 - point1: X_Y, (-4.0130858421, -2.3096354008)
 - point2: X_Y, (4.0234375, -0.9031249881)
 - expand: Real, 0.0
 - invert: Bool, False
 - feather_x: Real, 0.0
 - feather_y: Real, 0.0
 - bevel: Real, 0.0
 - bevCircle: Bool, True
[-▊solid_color 'wall']
 - z_depth: Real, 0.0
 - amount: Real, 1.0
 - blend_method: Integer, 0
 - color: Color, #ffffff
""".lstrip()

BLANK_CIRCLE="""
<layer type="circle" active="true" exclude_from_rendering="false" version="0.2">
  <param name="z_depth">
    <real value="0.0000000000"/>
  </param>
  <param name="amount">
    <real value="1.0000000000"/>
  </param>
  <param name="blend_method">
    <integer value="0" static="true"/>
  </param>
  <param name="color">
    <color>
      <r>1.000000</r>
      <g>1.000000</g>
      <b>1.000000</b>
      <a>1.000000</a>
    </color>
  </param>
  <param name="radius">
    <real value="1.0000000000"/>
  </param>
  <param name="feather">
    <real value="0.0000000000"/>
  </param>
  <param name="origin">
    <vector>
      <x>0.0000000000</x>
      <y>0.0000000000</y>
    </vector>
  </param>
  <param name="invert">
    <bool value="false"/>
  </param>
</layer>
""".lstrip()

CIRCLES = {
        'Black circle', 'Maybe white circle', 'Blue circle',
        'Purple circle', 'Orange circle', 'Green circle',
        'Yellow circle', 'Red circle',
        }

if __name__=='__main__':
    test_layer_items(dump = True)
