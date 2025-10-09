import bs4
from sangfroid.value.value import Value

@Value.handles_type()
class Canvas(Value):
    """
    A two-dimensional scene. All groups have a Canvas, including the
    top-level Animation itself.

    Only Layers can be the children of a Canvas. Attempting to add
    anything else will give you a ValueError.
    """
    @property
    def value(self):

        from sangfroid.layer.layer import Layer

        layers = [field
                 for field in self._tag.children
                 if isinstance(field, bs4.element.Tag)
                 ]
        if len([n for n in layers if n.name!='layer'])!=0:
            raise ValueError(
                    f"Only layers can be the children of a canvas: {self._tag}"
                    )

        result = [Layer.from_tag(layer) for layer in layers]

        return result

    @value.setter
    def value(self, v):

        from sangfroid.layer.layer import Layer

        self._tag.clear()

        for layer in v:
            if not isinstance(layer, Layer):
                raise TypeError(type(layer))
            self._tag.append(layer)
            self._tag.append("\n")
