"""."""

from collections import namedtuple

import sqlite3

from foodplan.macros.macro import Macro
from foodplan.macros.serving import Serving

# date changed for updated foods?


tables = {
    "consumed": [
        ("date", "text"),
        ("name", "text"),
        ("food_time", "text"),
        ("serving_type", "text"),
        ("serving_size", "integer")],
    "body": [
        ("date", "text"),
        ("weight", "real"),
        ("bodyfat", "integer"),
        ("adjust", "integer"),
        ("activity_level", "real")],
    "food": [
        ("name", "text"),
        ("serving_size", "integer"),
        ("f", "real"),
        ("p", "real"),
        ("k", "real"),
        ("a", "real")],
    "recipe": [],

    # to store arbitrary information, like crc strings
    "keyvalue": [
        ("key", "text"),
        ("value", "text")
    ]
}


ConsumedRecord = namedtuple(
    'ConsumedRecord',
    ', '.join(k for k, v in tables['consumed']))

FoodRecord = namedtuple(
    'FoodRecord',
    ', '.join(k for k, v in tables['food']))

KeyvalueRecord = namedtuple(
    'KeyvalueRecord',
    ', '.join(k for k, v in tables['keyvalue']))

BodyRecord = namedtuple(
    'BodyRecord',
    ', '.join(k for k, v in tables['body']))


def macros_from_consumed(record_iter, db):
    """Return kcals from ConsumedRecords iterator."""
    m_total = Macro(serving_size=0)
    for record in record_iter:
        food_record = db.food(record.name)

        m = Macro.RecordFactory(food_record)
        m.set_serving(
            Serving(size=record.serving_size, kind=record.serving_type))
        m_total += m
    return m_total


def delete_insert_consumed(consumed, db):
    """Deletes rows of same date as rows inserted."""
    # rows have to be deleted first to prevent manyfold doubles
    # if :consumed is generator
    consumed_2 = []
    dates = set()
    for record in consumed:
        dates.add((record.date,))
        consumed_2.append(record)

    with db.conn:
        db.conn.executemany(
            "DELETE FROM consumed WHERE date=?", dates)
    db.insert_consumed(consumed_2)


def delete_insert_bodies(bodies, db):
    """Deletes rows of same date as rows inserted."""
    # rows have to be deleted first to prevent manyfold doubles
    # if :consumed is generator
    bodies_2 = []
    dates = set()
    for record in bodies:
        dates.add((record.date,))
        bodies_2.append(record)

    with db.conn:
        db.conn.executemany(
            "DELETE FROM body WHERE date=?", dates)
    db.insert_bodies(bodies_2)


class DB(object):
    """."""

    def __init__(self, location=':memory:'):
        """."""
        self.conn = sqlite3.connect(location)
        self._build_tables()

    def __getitem__(self, name):
        """."""
        name, serving_size, f, p, k, a = self.food(name)

        macro = Macro(f=f, p=p, k=k, a=a, serving_size=serving_size)
        macro.name = name

        return macro

    def insert_consumed(self, consumed):
        """Insert consumed data into the DB.

        Input must be an iterable, containing ConsumedRecords"""
        with self.conn:
                self.conn.executemany(
                    "INSERT INTO consumed VALUES (?,?,?,?,?)", consumed)

    def insert_bodies(self, bodies):
        """Insert body data into the DB.

        Input must be an iterable, containing BodyRecords"""
        with self.conn:
                self.conn.executemany(
                    "INSERT INTO body VALUES (?,?,?,?,?)", bodies)

    def insert_food(self, food):
        """."""
        recipes = []
        db_inserts = []

        # for parsing recipes whose incredients are not in db yet
        local_db = {}

        # parse base items, save recipes for later
        for food_item in food:
            if food_item[0] == "base":
                name, f, p, k, a, serving_size = food_item[1]

                local_db[name] = Macro(
                    f=f, p=p, k=k, a=a, serving_size=serving_size)
                db_inserts.append((name, f, p, k, a, serving_size))

            elif food_item[0] == "recipe":
                recipes.append(food_item[1])

        # parse the recipes
        for recipe in recipes:
            name, servings, incredients = recipe
            r = Macro(serving_size=0)

            for incredient, serving in incredients.items():
                try:
                    m = self[incredient]
                except TypeError:
                    m = local_db[incredient]
                m.set_serving(serving)

                r = r + m
            r.serving_size = r.size / servings

            db_inserts.append((name, *r.macros, r.serving_size))

        # insert into db
        # https://stackoverflow.com/a/38463024
        with self.conn:
            for name, f, p, k, a, serving_size in db_inserts:
                self.conn.execute(
                    ("UPDATE food SET serving_size=?, f=?, p=?, k=?, a=? "
                     "WHERE name=?"),
                    (serving_size, f, p, k, a, name))
                self.conn.execute(
                    ("INSERT INTO food (name, serving_size, f, p, k, a) "
                     "SELECT ?,?,?,?,?,? WHERE (SELECT Changes() = 0)"),
                    (name, serving_size, f, p, k, a))

    def food(self, name):
        """Returns FoodRecord."""
        sel = """SELECT * FROM food AS f WHERE f.name = ?"""

        with self.conn:
            query = self.conn.execute(sel, (name,))
            for record in map(FoodRecord._make, query.fetchall()):
                return record

    def body(self, date):
        """Return the most recent BodyRecord earlier than :date."""
        sel = "SELECT * FROM body WHERE date <= ? ORDER BY date DESC LIMIT 1"

        with self.conn:
            query = self.conn.execute(sel, (date,))
            rows = query.fetchall()

            if rows:
                return BodyRecord._make(rows[0])

            # date before the first body measurement, take the earliest one
            sel = "SELECT * FROM body ORDER BY date ASC LIMIT 1"

            query = self.conn.execute(sel)
            rows = query.fetchall()

            if rows:
                return BodyRecord._make(rows[0])
            else:
                raise()

    def consumed(self, date):
        """."""
        sel = """SELECT * FROM consumed AS c WHERE c.date = ?"""

        with self.conn:
            query = self.conn.execute(sel, (date,))
            for record in map(ConsumedRecord._make, query.fetchall()):
                yield record

    def get_key(self, key):
        """Get value from key-value store by key.

        Return value if in DB, else None"""
        sel = "SELECT value FROM keyvalue WHERE key=?"
        with self.conn:
            for row in self.conn.execute(sel, (str(key),)):
                return str(row[0])
        return None

    def set_key(self, key, value):
        """Set key-value pair as strings.

        Return key, value tuple"""
        sel_update = "UPDATE keyvalue SET value=? WHERE key=?"
        sel_insert = (
            "INSERT INTO keyvalue (value, key) SELECT ?,? "
            "WHERE (SELECT Changes() = 0)")
        with self.conn:
            self.conn.execute(sel_update, (str(value), str(key)))
            self.conn.execute(sel_insert, (str(value), str(key)))
        return str(key), str(value)

    def _build_tables(self):
        """."""
        commands = []
        for k, v in tables.items():
            if v:
                colomns = ", ".join(
                    "{} {}".format(name, type_) for name, type_ in v)

                table_create = "CREATE TABLE IF NOT EXISTS {} ({})".format(
                    k, colomns)
                commands.append(table_create)

        with self.conn:
            for com in commands:
                self.conn.execute(com)
