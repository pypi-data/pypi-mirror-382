import os
import sangfroid
import gzip
import pytest
from test import *
from bs4 import BeautifulSoup

GZIP_HEADER = b'\x1f\x8b'

def test_animation_load_sif():
    sif = get_animation('circles.sif')

    assert sif.tag is not None
    assert sif.name == 'Circles'
    assert sif.desc == 'I like circles. They are round.'
    assert sif.width == 480
    assert sif.height == 270
    assert sif.xres == 2834.645669
    assert sif.yres == 2835.0
    assert sif.bgcolor==sangfroid.value.Color('#808080')
    assert sif.begin_time==0
    assert sif.end_time==sangfroid.T('5s', ref=sif.tag)

def test_animation_load_sifz():
    sif = get_animation('wombats.sifz')

    assert sif.name == 'wombats'
    assert sif.desc == 'I like wombats. They live in Australia.'

def normalise_xml(s):
    # This function used to strip out all space around NavigableStrings
    # and return the changed XML. But that's almost impossible to read
    # in pytest's output. So now it returns a list of:
    #  - for NavigableStrings: the stripped form of item.text
    #           (except that if the stripped form is the empty string,
    #           it's are silently dropped);
    #  - for everything else: lists of name and attributes.

    if s.startswith(GZIP_HEADER):
        s = gzip.decompress(s)

    if isinstance(s, (str, bytes)):
        s = BeautifulSoup(s, features='xml')

    result = []

    for item in s.descendants:
        if isinstance(item, bs4.NavigableString):
            s = item.text.strip()
            if s!='':
                result.append(s)
        elif not item.attrs:
            result.append(item.name)
        else:
            addendum = (
                    item.name + ' ' +
                    ' '.join([
                        f'{k}={v}'
                        for k,v
                        in sorted(item.attrs.items())
                        ]))

            result.append(addendum)

    return result

def test_animation_save_and_saveas():

    with open(os.path.join(
        os.path.dirname(__file__),
        'circles.sif',
        ), 'rb') as f:

        original = f.read()

    with open(os.path.join(
        os.path.dirname(__file__),
        f'purple-circles.sif',
        ), 'rb') as f:

        expected = f.read()

    expected = normalise_xml(expected)

    for compress_source in [False, True]:

        for save_as in [False, True]:

            # Firstly, let's set up the source file that we're
            # going to read back in.

            if compress_source:
                source_suffix = '.sifz'
                source_contents = gzip.compress(original)
            else:
                source_suffix = '.sif'
                source_contents = original

            source_filename = temp_filename(suffix=source_suffix)

            # For assertion messages:
            details = (
                    f'compress_source={compress_source}; '
                    f'save_as={save_as}; '
                    f'source_filename={source_filename}'
                    )

            with open(source_filename, 'wb') as f:
                f.write(source_contents)

            # Right. Now, what happens when we load it, make
            # some changes, and write it out again?

            animation = sangfroid.open(source_filename)

            for circle in animation.find_all('circle'):
                circle['color'].value = '#ff00ff'

            if save_as:
                final_filename = temp_filename()
                details += f'; final_filename={final_filename}'
                animation.save(final_filename)
            else:
                final_filename = source_filename
                animation.save()

            assert os.path.isfile(final_filename), (
                    f"save created a file ({details})"
                    )
            assert os.path.getsize(final_filename)!=0, (
                    f"savefile is not empty ({details})"
                    )

            with open(final_filename, 'rb') as f:
                found = f.read()

            found = normalise_xml(found)

            assert found==expected, (
                    f'{details}; final_filename={final_filename}'
                    )

            os.unlink(source_filename)
            if final_filename!=source_filename:
                os.unlink(final_filename)

def test_animation_saveas_different_format():

    def format_for(suffix):
        if suffix=='sif':
            return sangfroid.format.Sif
        elif suffix=='sifz':
            return sangfroid.format.Sifz
        else:
            raise ValueError(suffix)

    for read_from, write_to in [
            ('sif',  'sif' ),
            ('sif',  'sifz'),
            ('sifz', 'sif' ),
            ('sifz', 'sifz'),
            ]:

        if read_from=='sif':
            source_filename = 'circles.sif'
        elif read_from=='sifz':
            source_filename = 'wombats.sifz'
        else:
            raise ValueError(source_filename)

        source = sangfroid.open(
                os.path.join(
                    os.path.dirname(__file__),
                    source_filename,
                    ))
        assert isinstance(source._format, format_for(read_from))

        tempname = temp_filename(
                suffix=f'.{write_to}')

        source.save(filename=tempname)

        revenant = sangfroid.open(tempname)

        assert source.desc==revenant.desc
        assert isinstance(source._format, format_for(write_to))

        os.unlink(tempname)

def test_animation_framecount():
    sif = get_animation('bouncing.sif')
    assert sif.framecount==121

def test_animation_blank_simple():

    sif = sangfroid.Animation()
    blank_sif_assertions(sif, 'simple')

def blank_sif_assertions(sif, name):

    assert sif.name == 'New animation', name
    assert sif.desc == '', name
    assert sif.width == 480, name
    assert sif.height == 270, name
    assert sif.xres == 2834.645669
    assert sif.yres == 2834.645669
    assert sif.bgcolor==sangfroid.value.Color('#808080'), name
    assert sif.begin_time==0, name
    assert sif.end_time==sangfroid.T('5s', ref=sif.tag), name

    keyframes = list(sif.keyframes)
    assert len(keyframes)==1, name
    assert keyframes[0].time==0, name

def test_animation_blank_save():
    sif = sangfroid.Animation()
    
    names = {
            'uncompressed': temp_filename(suffix='.sif'),
            'compressed': temp_filename(suffix='.sifz'),
            }

    with pytest.raises(ValueError):
        sif.save()

    for n in names.values():
        sif.save(n)

    for name, filename in names.items():
        sif2 = sangfroid.Animation(filename)
        blank_sif_assertions(sif2, name)

def test_animation_append():

    outer = sangfroid.Animation()

    inner = sangfroid.layer.Group()
    outer.append(inner)

    sequence = []

    for n in outer._tag.find_all(recursive=False):
        if sequence and sequence[-1]==n.name:
            continue
        sequence.append(n.name)

    assert sequence==['name', 'meta', 'keyframe', 'layer'], (
            'Layers are added after the metadata in animations'
            )

def test_animation_tagattr_underscores():
    """
    Regression test: TagAttrFields translate underscores
    in their names to hyphens.
    """
    sif = get_animation('bouncing.sif')

    TOPLEVEL_ATTRS = [
            'antialias',
            'begin-time',
            'bgcolor',
            'end-time',
            'fps',
            'gamma-b',
            'gamma-g',
            'gamma-r',
            'height',
            'version',
            'view-box',
            'width',
            'xres',
            'yres',
            ]

    def check_toplevel_attrs(sif):
        assert sorted(sif.tag.attrs.keys())==TOPLEVEL_ATTRS

    check_toplevel_attrs(sif)

    sif.gamma_r = 0
    check_toplevel_attrs(sif)

    sif.gamma_g = 0
    check_toplevel_attrs(sif)

    sif.gamma_b = 0
    check_toplevel_attrs(sif)

    sif.view_box = '-4.0 2.25 4.0 -2.25'
    check_toplevel_attrs(sif)

    sif.begin_time = 0
    check_toplevel_attrs(sif)

    sif.end_time = 0
    check_toplevel_attrs(sif)

def test_animation_bgcolor():
    sif = get_animation('circles.sif')

    assert sif.tag['bgcolor'] == "0.500000 0.500000 0.500000 1.000000"
    assert sif.bgcolor.as_tuple()==(0.5, 0.5, 0.5, 1.0)
    sif.bgcolor = (255, 165, 0, 77)
    assert sif.tag['bgcolor'] == "1.000000 0.647059 0.000000 0.301961"
    assert sif.bgcolor.as_tuple()==(1.0, 0.647059, 0.0, 0.301961)
