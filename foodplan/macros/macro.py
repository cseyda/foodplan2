"""."""

import numpy as np

from .serving import Serving, ServingType


class Macro(object):
    """."""

    macro_kcals = np.array([[9], [4], [4], [7]])

    def __init__(self, *, f=0.0, p=0.0, k=0.0, a=0.0,
                 serving_size=100, serving=None, name=""):
        """."""
        self.macros = np.array([f, p, k, a])

        # standard serving_size
        self.serving_size = serving_size

        # f, p, k are the actual nutritional values in gr
        self.size = self._get_gr_from_serving(serving)

        self.name = name

    def _get_gr_from_serving(self, serving, init_size=0):
        """."""
        if serving:
            if serving.kind == ServingType["gr"]:
                init_size += serving.size
            else:
                init_size += serving.size * self.serving_size
        else:
            init_size += self.serving_size
        return init_size

    def add_serving(self, serving):
        """Add Serving to size.

        Input:
            Serving or int (for gr)

        Output:
            self
        """
        self.size = self._get_gr_from_serving(serving, self.size)
        return self

    def set_serving(self, serving):
        """Set Serving as new size.

        Input:
            Serving or int (for gr)

        Output:
            self
        """
        self.size = self._get_gr_from_serving(serving)
        return self

    def __add__(self, other):
        """Addition, size and macros, return new object.

        serving_size is set to 100
        """
        size = self.size + other.size
        macros = (self.macros * self.size + other.macros * other.size)
        if size:
            macros /= size

        return Macro(f=macros[0], p=macros[1], k=macros[2], a=macros[3],
                     serving_size=100, serving=Serving(size, "gr"))

    @property
    def f(self):
        """."""
        return self.macros[0] * self.size / 100

    @property
    def p(self):
        """."""
        return self.macros[1] * self.size / 100

    @property
    def k(self):
        """."""
        return self.macros[2] * self.size / 100

    @property
    def a(self):
        """."""
        return self.macros[3] * self.size / 100

    @property
    def kcals(self):
        """."""
        return self.kcals_100 * self.size / 100

    @property
    def kcals_100(self):
        """."""
        return self.macros.dot(self.macro_kcals)[0]

    def __repr__(self):
        """."""
        return " ".join([str(self.f), str(self.p), str(self.k),
                         "kcals:", str(self.kcals),
                         "size:", str(self.size),
                         "kcals_100:", str(self.kcals_100),
                         str(self.macros)])
