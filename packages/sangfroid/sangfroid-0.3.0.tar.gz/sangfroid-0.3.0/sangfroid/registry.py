"""
Here we connect things to the code which handles them.
End users don't have to worry about this.
"""

from sangfroid.util import normalise_synfig_layer_type_name
from typing import Any

class Registry:
    """
    Decorator, mapping names of things onto classes that handle those things.

    Names are case-insensitive, and underscores are not significant.

    """
    def __init__(self):
        self.handlers = {}

    # Decorator.
    def __call__(self, name:(str|None)=None):
        """
        Args:
            name: the name to associate this class with.
                If None or omitted, the name of the class is used.
        """
        def _inner(c):
            n = name or c.__name__
            n = normalise_synfig_layer_type_name(n)

            self.handlers[n] = c
            return c
        return _inner

    def from_name(self, name:str) -> Any:
        """
        Returns whatever is associated with "name".

        Raises:
            KeyError: if the name doesn't refer to anything.
        """
        name = normalise_synfig_layer_type_name(name)

        if name not in self.handlers:
            raise KeyError(
                    f"This tag is a {name}, which I don't know how "
                    "to handle.\n\n"
                    "Here are the things I do know:\n"
                    f"  {' '.join(sorted(self.handlers.keys()))}"
                    )
        result = self.handlers[name]

        return result
