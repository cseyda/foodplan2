"""Test for DB."""

import sys
import unittest
import logging

import tempfile

import yaml

from foodplan.db.db import DB
from foodplan.input.input import _yield_food_items, _yield_consumed_items

from foodplan.macros.macro import Macro
from foodplan.macros.serving import Serving


class TestDB(unittest.TestCase):

    def setUp(self):
        """."""
        self.db = DB()

        with open("tests/fixtures/db_consumed.yaml", "r") as f:
            consumed_yaml = yaml.safe_load(f)
        with open("tests/fixtures/db_food.yaml", "r") as f:
            food_yaml = yaml.safe_load(f)

        self.consumed = [_ for _ in _yield_consumed_items(consumed_yaml)]
        self.food = [_ for _ in _yield_food_items(food_yaml)]

    def test_insert(self):
        """."""
        with self.db.conn:
            self.db.conn.executemany(
                "INSERT INTO consumed VALUES (?,?,?,?,?)", self.consumed)

        self.db.insert_food(self.food)

    def test_query(self):
        """."""
        log = logging.getLogger("TestDB.test_query")
        self.test_insert()

        kcals = {}

        with self.db.conn:
            # for row in conn.execute("SELECT * FROM consumed"):
            #    print(row)
            # for row in self.db.conn.execute("SELECT * FROM food"):
            #    # print(row)
            #    log.debug("row= %r", row)

            for row in self.db.conn.execute("""
        SELECT c.date, c.serving_type, c.serving_size,
         f.f, f.p, f.k, f.a, f.serving_size
         FROM consumed as c, food as f
         WHERE c.name = f.name"""):
                if row[0] not in kcals:
                    kcals[row[0]] = Macro(serving_size=0)

                m = Macro(f=row[3], p=row[4], k=row[5], a=row[6],
                          serving_size=row[7])
                m.set_serving(Serving(row[2], row[1]))

                kcals[row[0]] += m

            log.debug("kcals= %r", kcals)

        kcals_list = [(date, macros) for date, macros in kcals.items()]
        for date, macros in kcals_list[1:]:
            self.assertEqual(kcals_list[0][1], macros)

    def test_food(self):
        """."""
        # log = logging.getLogger("TestDB.test_food")
        self.test_insert()

        for con in self.consumed:
            self.db.food(con[1])

    def test_initialization(self):
        """Test initialization with real files."""
        with tempfile.NamedTemporaryFile() as fp:
            DB(fp.name)
            DB(fp.name)

    def test_getattr(self):
        """Test [] access."""
        self.test_insert()

        for name in ['mandeln', 'fisch', 'knäckebrot', 'rice_white', 'apfel',
                     'ei', 'müsli_riegel', 'knäckebrot', 'fisch_rice']:
            print(name, self.db[name])

    def tearDown(self):
        """."""
        pass


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("TestDB.test_query").setLevel(logging.DEBUG)

    unittest.main(buffer=False)
