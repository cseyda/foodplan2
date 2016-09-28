"""Test for DB."""

import sys
import unittest
import logging
import math

import tempfile

import yaml

from foodplan.db.db import DB, delete_insert_consumed
from foodplan.db.db import macros_from_consumed

from foodplan.input.input import _yield_food_items, _yield_consumed_items
from foodplan.input.input import _yield_body_items

# from foodplan.macros.macro import Macro
# from foodplan.macros.serving import Serving


with open("tests/fixtures/db_consumed.yaml", "r") as f:
    consumed_yaml = yaml.safe_load(f)
_consumed = [_ for _ in _yield_consumed_items(consumed_yaml)]

with open("tests/fixtures/db_food.yaml", "r") as f:
    food_yaml = yaml.safe_load(f)
_food = [_ for _ in _yield_food_items(food_yaml)]

with open("tests/fixtures/db_body.yaml", "r") as f:
    body_yaml = yaml.safe_load(f)
_body = [_ for _ in _yield_body_items(body_yaml)]


class TestDB(unittest.TestCase):

    def setUp(self):
        """."""
        self.db = DB()

    def test_insert(self):
        """."""
        self.db.insert_consumed(_consumed)
        self.db.insert_food(_food)
        self.db.insert_bodies(_body)

    def test_initialization(self):
        """Test initialization with real files."""
        with tempfile.NamedTemporaryFile() as fp:
            DB(fp.name)
            DB(fp.name)

    def tearDown(self):
        """."""
        pass


class TestConsumed(unittest.TestCase):

    def setUp(self):
        """."""
        self.db = DB()

    def test_insert(self):
        """."""
        self.db.insert_consumed(_consumed)
        self.db.insert_food(_food)
        # self.db.insert_bodies(_body)

    def test_consumed_query(self):
        """."""
        self.db.insert_consumed(_consumed)
        self.db.insert_food(_food)

        m0 = macros_from_consumed(self.db.consumed("20160903"), self.db)
        m1 = macros_from_consumed(self.db.consumed("20160904"), self.db)
        m2 = macros_from_consumed(self.db.consumed("20160905"), self.db)
        self.assertEqual(m1, m2)
        self.assertNotEqual(m0, m1)

    def test_delete_insert_consumed(self):
        """."""
        self.db.insert_consumed(_consumed)
        self.db.insert_food(_food)

        m1 = macros_from_consumed(self.db.consumed("20160904"), self.db)

        self.db.insert_consumed(_consumed)
        m2 = macros_from_consumed(self.db.consumed("20160904"), self.db)

        self.assertNotEqual(m1, m2)

        delete_insert_consumed(_consumed, self.db)
        m3 = macros_from_consumed(self.db.consumed("20160904"), self.db)
        self.assertEqual(m1, m3)


class TestFood(unittest.TestCase):

    def setUp(self):
        """."""
        self.db = DB()
        self.rows = {
            'mandeln': {'f': 50, 'p': 21.7, 'k': 9.4, 'size': 100},
            'fisch': {'f': 3, 'p': 20, 'k': 0, 'size': 100},
            'knäckebrot': {'f': 0.26, 'p': 1.17, 'k': 7.8, 'size': 13},
            'rice_white': {'f': 1, 'p': 8.5, 'k': 97.5, 'size': 125},
            'apfel': {'f': 0.15, 'p': 0.45, 'k': 17.1, 'size': 150},
            'ei': {'f': 6.6, 'p': 7.74, 'k': 0.3, 'size': 60},
            'müsli_riegel': {'f': 1.98, 'p': 1.43, 'k': 14.74, 'size': 22},
            'fisch_rice': {'f': 3.53, 'p': 24.53, 'k': 52, 'size': 166.66}
        }

    def test_insert(self):
        """."""
        # self.db.insert_consumed(_consumed)
        self.db.insert_food(_food)
        # self.db.insert_bodies(_body)

    def test_getattr(self):
        """Test [] access."""
        self.db.insert_food(_food)

        for name in ['mandeln', 'fisch', 'knäckebrot', 'rice_white', 'apfel',
                     'ei', 'müsli_riegel', 'fisch_rice']:
            m = self.db[name]
            row = self.rows[name]

            for attr in ["f", "p", "k", "size"]:
                self.assertTrue(
                    math.isclose(getattr(m, attr), row[attr], abs_tol=0.01))


class TestBody(unittest.TestCase):

    def setUp(self):
        """."""
        self.db = DB()

    def test_insert(self):
        """."""
        # self.db.insert_consumed(_consumed)
        # self.db.insert_food(_food)
        self.db.insert_bodies(_body)

    def test_body(self):
        """."""
        self.test_insert()

        dates = ["20160924", "20160917", "20160910", "20160903",
                 "20160827", "20160827"]
        for d in dates:
            self.assertEqual(d, self.db.body(d).date)

        dates_inbetween = ["20160927", "20160919", "20160912", "20160905",
                           "20160829", "20160825"]
        for d, d_test in zip(dates_inbetween, dates):
            self.assertEqual(d_test, self.db.body(d).date)


class TestKeyval(unittest.TestCase):

    def setUp(self):
        """."""
        self.db = DB()

    def test_keyval(self):
        """."""
        key = "test"
        value = "value"

        self.db.set_key(key, value)
        value2 = self.db.get_key(key)

        self.assertEqual(value, value2)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    # logging.getLogger("TestDB.test_query").setLevel(logging.DEBUG)

    unittest.main(buffer=False)
