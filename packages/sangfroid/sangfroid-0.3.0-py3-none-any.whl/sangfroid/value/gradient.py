import bs4
from sangfroid.value.value import Value
from sangfroid.value.color import Color

@Value.handles_type()
class Gradient(Value):
    @property
    def value(self):
        colours = self._tag.find_all('color')
        if len(colours)<2:
            self._raise_colour_count_error()

        result = dict([
                (float(c['pos']), Color(c)) for c in colours
                ])

        return result

    @value.setter
    def value(self, v):
        if isinstance(v, Gradient):
            v = v.value

        if not isinstance(v, dict):
            raise TypeError("Gradient.value must be a dict")

        if len(v)<2:
            self._raise_colour_count_error()

        self._tag.clear()

        for pos, colour in sorted(v.items()):

            colour_tag = Color(colour).tag
            colour_tag['pos'] = '%.06g' % (pos,)
            self._tag.append(colour_tag)

    def _raise_colour_count_error(self):
        raise ValueError("there should be at least two colours in a gradient")

    def __len__(self):
        return len(self.value)

    def __getitem__(self, n):
        return self.value[n]

    def __setitem__(self, n, v):
        previous = self.value
        previous[n] = v
        self.value = previous

    def keys(self):
        return self.value.keys()

    def values(self):
        return self.value.values()

    def items(self):
        return self.value.items()

    def __iter__(self):
        yield from iter(self.value)

    def __str__(self):
        return (
                '{' +
                ','.join([f'{k}:{v}' for k,v in self.items()]) +
                '}')

    def as_python_expression(self):
        return (
                '{' +
                ','.join([f'{k}:{v.as_python_expression()}'
                          for k,v in self.items()]) +
                '}')

        return str(self)
