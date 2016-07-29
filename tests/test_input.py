"""."""

import unittest
from pathlib import Path

from foodplan.input.input import load_yaml

from foodplan.input.input import get_food_from_file
from foodplan.input.input import get_consumed_from_file

from foodplan.input.input import pickled_load_food
from foodplan.input.input import pickled_load_consumed

import cProfile, pstats, io
import time


class TestInput(unittest.TestCase):
    """."""

    def setUp(self):
        """."""
        self.food_path = Path("tests/resources/food.yaml")
        self.consumed_path = Path("tests/resources/consumed.yaml")
        self.body_path = Path("tests/resources/body.yaml")

        self.food = pickled_load_food(self.food_path,
            Path("tests/resources/crc.pickle"),
            Path("tests/resources/food.pickle"))

    def tearDown(self):
        """."""
        pass

    def test_food(self):
        """."""
        start = time.time()
        for i in range(1, 5):
            food = get_food_from_file(self.food_path)
        print("food took", time.time()-start, "s")

        start = time.time()
        for i in range(1, 5):
            food = pickled_load_food(
                self.food_path,
                Path("tests/resources/crc.pickle"),
                Path("tests/resources/food.pickle"))
        print("pickled food took", time.time()-start, "s")

    def test_consumed(self):
        """."""
        start = time.time()
        for i in range(1, 5):
            consumed_db = get_consumed_from_file(self.consumed_path, self.food)
        print("consumed took", time.time()-start, "s")

        start = time.time()
        for i in range(1, 5):
            consumed_db = pickled_load_consumed(
                self.consumed_path, self.food, 0,
                Path("tests/resources/crc.pickle"),
                Path("tests/resources/consumed.pickle"))

        print("pickled consumed took", time.time()-start, "s")


if __name__ == '__main__':
    unittest.main()
