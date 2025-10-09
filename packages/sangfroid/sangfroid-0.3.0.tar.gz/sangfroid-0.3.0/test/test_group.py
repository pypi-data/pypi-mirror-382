import sangfroid
from test import *
import pytest

def test_canvas_children():
    sif = get_animation('circles.sif')

    EXPECTED = [
            "[🔵circle 'Red circle']",
            "[📂group 'More circles']",
            "[📂group \"Well, it's round\"]",
            "[📂group 'Blurry circle']",
            "[📂group 'Background circle']",
            ]

    found = [str(layer) for layer in sif.children]

    assert found==EXPECTED

def test_canvas_descendants():
    sif = get_animation('circles.sif')

    EXPECTED = [
            "[🔵circle 'Red circle']",
            "[📂group 'More circles']",
            "[-🔵circle 'Yellow circle']",
            "[-📂group 'All right, one more circle']",
            "[-🔵circle 'Orange circle']",
            "[📂group \"Well, it's round\"]",
            "[-🔵circle 'Purple circle']",
            "[📂group 'Blurry circle']",
            "[-🟠blur 'Blur']",
            "[-🔵circle 'Blue circle']",
            "[📂group 'Background circle']",
            "[-🔵circle 'Maybe white circle']",
            "[-🔵circle 'Black circle']",
            ]

    found = [str(layer) for layer in sif.descendants]

    assert found==EXPECTED

def test_group_append():
    sif = get_animation('bouncing.sif')

    assert [repr(c) for c in sif.children]==[
            "[🕰️timeloop]",
            "[📂group 'Ball']",
            "[📂group 'Shadow']",
            "[📂group 'Background']",
            ]

    sif.append(sangfroid.layer.Text("Another one!"))

    assert [repr(c) for c in sif.children]==[
            "[🕰️timeloop]",
            "[📂group 'Ball']",
            "[📂group 'Shadow']",
            "[📂group 'Background']",
            "[𝕋text 'Another one!']",
            ]

def test_group_insert():
    sif = get_animation('bouncing.sif')

    sif.insert(1, sangfroid.layer.Text("Another one!"))

    assert [repr(c) for c in sif.children]==[
            "[🕰️timeloop]",
            "[𝕋text 'Another one!']",
            "[📂group 'Ball']",
            "[📂group 'Shadow']",
            "[📂group 'Background']",
            ]

    sif = get_animation('bouncing.sif')

    sif.insert(-1, sangfroid.layer.Text("Another one!"))

    assert [repr(c) for c in sif.children]==[
            "[🕰️timeloop]",
            "[📂group 'Ball']",
            "[📂group 'Shadow']",
            "[𝕋text 'Another one!']",
            "[📂group 'Background']",
            ]

    sif.insert(-2, sangfroid.layer.Circle())

    assert [repr(c) for c in sif.children]==[
            "[🕰️timeloop]",
            "[📂group 'Ball']",
            "[📂group 'Shadow']",
            '[🔵circle]',
            "[𝕋text 'Another one!']",
            "[📂group 'Background']",
            ]

def test_group_len():
    # note that Animation is a subclass of Group
    sif = sangfroid.Animation()

    assert len(sif)==0
    assert len(sif.items())==0

    text = sangfroid.layer.Text('Hello world!')

    with pytest.raises(NotImplementedError):
        # back to front
        text.append(sif)

    sif.append(text)

    assert len(sif)==1
    assert len(sif.items())==0
    assert isinstance(sif[0], sangfroid.layer.Text)
    assert sif[0].text=='Hello world!'

    sif.append(sangfroid.layer.Circle())

    assert len(sif)==2
    assert len(sif.items())==0
    assert isinstance(sif[0], sangfroid.layer.Text)
    assert isinstance(sif[1], sangfroid.layer.Circle)

def test_group_iteration():

    g = sangfroid.layer.Group()

    for i in range(4):
        g.append(
                sangfroid.layer.Text(f"Text layer {i}")
                )

    found = [layer.text for layer in g]

    assert found==[
            'Text layer 0',
            'Text layer 1',
            'Text layer 2',
            'Text layer 3',
            ]
