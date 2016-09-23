"""."""

import sqlite3

from foodplan.macros.macro import Macro
# from foodplan.macros.serving import Serving

# consumed:
# date, food_name, food_time, serving_type, serving_size

# date changed for updated foods?

# food:
# food_name, serving_size, f, p, k, a


class DB(object):
    """."""
    tables = {
        "consumed": [
            ("date", "text"),
            ("name", "text"),
            ("food_time", "text"),
            ("serving_type", "text"),
            ("serving_size", "integer")],
        "body": [],
        "food": [
            ("name", "text"),
            ("serving_size", "integer"),
            ("f", "real"),
            ("p", "real"),
            ("k", "real"),
            ("a", "real")],
        "recipe": [],
        "keyvalue": [
            ("key", "text"),
            ("value", "text")
        ]
    }

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
        """."""
        with self.conn:
                self.db.conn.executemany(
                    "INSERT INTO consumed VALUES (?,?,?,?,?)", consumed)

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
        """Returns tuple (name, serving_size, f, p, k, a)."""
        sel = """SELECT * FROM food AS f WHERE f.name = ?"""

        with self.conn:
            for row in self.conn.execute(sel, (name,)):
                return row

    def body(self):
        """."""
        pass

    def consumed(self):
        """."""
        pass

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
            self.conn.execute(sel_update, (str(key), str(value)))
            self.conn.execute(sel_insert, (str(key), str(value)))
        return str(key), str(value)

    def _build_tables(self):
        """."""
        # except sqlite3.OperationalError as e:
        #    error_text = e.args[0].split()
        #    if error_text[0] != 'table' \
        #            or error_text[2:] != ['already', 'exists']:
        #        raise(e)
        commands = []
        for k, v in self.tables.items():
            if v:
                colomns = ", ".join(
                    "{} {}".format(name, type_) for name, type_ in v)

                table_create = "CREATE TABLE IF NOT EXISTS {} ({})".format(
                    k, colomns)
                commands.append(table_create)

        with self.conn:
            for com in commands:
                self.conn.execute(com)
