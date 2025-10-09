"""
These represent the various formats for saving an animation.
End users shouldn't have to bother with them; we pick the right one
automatically based on the file magic.
"""

import gzip
import os
import bs4
from typing import Self

class Format:
    """
    A disk file, containing an animation saved in a particular format.

    It also allows access to files dependent on the main file.

    Attributes:
        filename (str): the filename.
        extensions (tuple of str): the filename extensions which
            can be used for this format, without leading dots.
            (Class field.)
        magic_number (bytes): the first two characters of
            files of this format.
            (Class field.)
    """

    def __init__(self):
        raise NotImplementedError(
                "Create formats using from_filename().")

    def main_file(self) -> bs4.Tag:
        """
        Returns the parsed XML of the main document.

        For the filename, see the `filename` field.
        """
        raise NotImplementedError()

    def __getitem__(self, v):
        """
        Looks up a file referred to by the main file.
        """
        return self._subfiles[v]

    def __len__(self) -> int:
        """
        Returns the number of files referred to in the main file.
        """
        return len(self._subfiles)

    def items(self):
        return self._subfiles.items()

    def keys(self):
        return self._subfiles.keys()

    def values(self):
        return self._subfiles.values()

    @classmethod
    def from_filename(cls,
                      filename:str,
                      load:bool = True,
                      ) -> Self:
        """
        Given a filename, returns a Format of the appropriate subclass,
        possibly loaded from the file of that name.

        Args:
            filename: the filename
            load: if True, load the file with that name

        Raises:
            ValueError: if the filename isn't in a format we know
                how to handle.
            FileNotFoundError: if load==True and the file doesn't
                exist.
        """
        assert filename is not None

        if load:
            with open(filename, 'rb') as f:
                magic = f.read(2)

            if not magic:
                raise ValueError("The file {filename} is empty.")

            handlers = [h for h in cls.handlers()
                        if h.magic_number==magic]
            if not handlers:
                raise ValueError(
                        f"The file {filename} isn't in a format I know how "
                        "to handle.")
        else:
            extension = os.path.splitext(filename)[1].lower()
            if extension.startswith('.'):
                extension = extension[1:]

            handlers = [h for h in cls.handlers()
                        if extension in h.extensions]
            if not handlers:
                raise ValueError(
                        "I don't know how to handle files with the "
                        f"extension {extension}."
                        )

        assert len(handlers)==1

        handler = handlers[0]

        result = handler.__new__(handler)
        result.filename = filename
        return result

    def save(self,
             content:bs4.BeautifulSoup,
             filename:(str|None)=None,
             ):
        """
        Saves a file to disk.

        Args:
            content: the XML document to save
            filename: the filename to save under;
                if None, we use self.filename; if not None,
                this is a "save as", so self.filename will
                be set to this value.
        """
        raise NotImplementedError()

    def _filename_for_saving(self, filename):
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename

        return filename

    def _write_to_file(self, f, content):
        f.write(str(content).encode('UTF-8'))

    @classmethod
    def handlers(cls) -> list:
        """
        Returns all known subclasses of Format.
        """
        return [
                h for h in globals().values()
                if isinstance(h, type)
                and issubclass(h, Format)
                and h!=Format
                ]

class FileContextHandler:
    def __init__(self, f):
        self.soup = bs4.BeautifulSoup(
                f,
                features = 'xml',
                )

    def __enter__(self):
        return self.soup

    def __exit__(self, exc_type, exc_value, traceback):
        pass

class Sif(Format):

    magic_number = b'<?' # start of XML doctype
    extensions = ('sif',)

    def main_file(self):
        return FileContextHandler(open(self.filename, 'r'))

    def save(self, content, filename=None):
        filename = self._filename_for_saving(filename)

        with open(filename, 'wb') as f:
            self._write_to_file(f, content)

class Sifz(Format):

    magic_number = b'\x1f\x8b' # gzip header
    extensions = ('sifz',)

    def main_file(self):
        return FileContextHandler(gzip.open(self.filename, 'r'))

    def save(self, content, filename=None):
        filename = self._filename_for_saving(filename)

        with gzip.open(filename, 'wb') as f:
            self._write_to_file(f, content)

class Sfg(Format):
    
    magic_number = b'PK' # zipfile header (RIP Phil Katz)
    extensions = ('sfg',)

    def main_file(self):
        raise ValueError(
                '.sfg is not yet supported. See: \n'
                'https://gitlab.com/marnanel/sangfroid/-/issues/2'
                )

class Blank(Format):
    """
    The blank animation you get if you instantiate Animation without
    a filename.

    Unlike most subclasses of Format, this can be instantiated
    directly.
    """

    magic_number = None
    extensions = tuple()

    def __init__(self):
        self.filename = None

    def main_file(self):
        return FileContextHandler(BLANK_ANIMATION)

    def save(self, *args, **kwargs):
        raise ValueError(
                'It makes no sense to save to new'
                )

BLANK_ANIMATION = """<?xml version="1.0" encoding="UTF-8"?>
<canvas
        version="1.2"
        width="480" height="270"
        xres="2834.645669" yres="2834.645669"
        gamma-r="1.000000" gamma-g="1.000000" gamma-b="1.000000"
        view-box="-4.000000 2.250000 4.000000 -2.250000"
        antialias="1" fps="24.000"
        begin-time="0f" end-time="5s"
        bgcolor="0.500000 0.500000 0.500000 1.000000"
        >
  <name>New animation</name>
  <meta name="background_first_color" content="0.880000 0.880000 0.880000"/>
  <meta name="background_rendering" content="0"/>
  <meta name="background_second_color" content="0.650000 0.650000 0.650000"/>
  <meta name="background_size" content="15.000000 15.000000"/>
  <meta name="grid_color" content="0.623529 0.623529 0.623529"/>
  <meta name="grid_show" content="0"/>
  <meta name="grid_size" content="0.250000 0.250000"/>
  <meta name="grid_snap" content="0"/>
  <meta name="guide_color" content="0.435294 0.435294 1.000000"/>
  <meta name="guide_show" content="1"/>
  <meta name="guide_snap" content="0"/>
  <meta name="jack_offset" content="0.000000"/>
  <meta name="onion_skin" content="0"/>
  <meta name="onion_skin_future" content="0"/>
  <meta name="onion_skin_keyframes" content="1"/>
  <meta name="onion_skin_past" content="1"/>
  <keyframe time="0f" active="true">start</keyframe>
</canvas>"""
