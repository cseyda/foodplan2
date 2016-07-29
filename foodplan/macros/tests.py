"""."""

import unittest

from foodplan.macros.macro import Macro
from foodplan.macros.serving import Serving

import cProfile, pstats, io


class TestMacro(unittest.TestCase):
    """."""

    def setUp(self):
        """."""
        self.m = Macro(
            f=1.0, p=1.0, k=1.0,
            serving=Serving(200, "gr"), name="m")

        self.n = Macro(
            f=2.0, p=3.0, k=4.0,
            serving_size=25, serving=Serving(2, "servings"), name="n")

    def tearDown(self):
        """."""
        pass

    def _compare_obj_to_dict(self, o, var):
        """Compare variables of an object with values of a dict."""
        for k, v in var.items():
            self.assertEqual(getattr(o, k), v)

    def test_initiation(self):
        """Test if Macro is initiated correctly."""
        # values the test objects should have
        test_vars = {
            "m": {"name": "m", "serving_size": 100, "size": 200},
            "n": {"name": "n", "serving_size": 25, "size": 50}}

        for obj_name, var in test_vars.items():
            o = getattr(self, obj_name)
            self._compare_obj_to_dict(o, var)

    def test_addition(self):
        """Test for proper addition. Macros, size, serving_size."""
        p = self.m + self.n

        self.assertEqual((p.f, p.p, p.k, p.a), (3.0, 3.5, 4.0, 0.0))
        self.assertEqual(
            (p.macros[0], p.macros[1], p.macros[2], p.macros[3]),
            (1.2, 1.4, 1.6, 0.0))

    def test_speed(self):
        """."""
        p = Macro(serving_size=0)
        pr = cProfile.Profile()
        pr.enable()

        for i in range(1, 1000):
            p += self.m + self.n

        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        # print(s.getvalue())
