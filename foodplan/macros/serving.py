"""."""

from enum import Enum
# from collections import namedtuple


ServingType = Enum("ServingType", "gr servings")
# ServingSize = namedtuple("ServingSize", "size type")


class Serving(object):
    """."""

    def __init__(self, size=1, kind="servings"):
        """."""
        self.size = size
        self.kind = ServingType[kind]

    def __repr__(self):
        """."""
        return "{} {}".format(str(self.size), ServingType(self.kind))
