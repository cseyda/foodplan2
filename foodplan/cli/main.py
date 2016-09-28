"""."""

from os import sys
from pathlib import Path
from datetime import date, datetime, timedelta

# import yaml

from foodplan.input.input import load_yaml, calc_crc
# from foodplan.input.input import load_body  # , get_consumed_from_file

from foodplan.input.output import print_consumed

from foodplan.db.db import DB
from foodplan.db.db import delete_insert_consumed, delete_insert_bodies

from foodplan.input.input import _yield_food_items, _yield_consumed_items
from foodplan.input.input import _yield_body_items


def _config(sys_cmd):
    """."""
    config_file_path = Path(sys_cmd[1])
    config_file = load_yaml(config_file_path)

    if "path" not in config_file:
        print("Config file needs entry :path: for location of files.")

    return {"path": Path(config_file["path"])}


def dates_till_next_sunday(days=8):
    """."""
    # get sonday and count backwards
    today = date.today()
    week_year, week_week, week_day = today.isocalendar()
    week_sunday = datetime.strptime(
        "{}-W{}-0".format(week_year, week_week), "%Y-W%W-%w")

    startdate = week_sunday - timedelta(days)
    for day in range(0, days + 1):
        yield startdate + timedelta(day)


def has_crc_changed(db, p, key):
    """Create CRC of :p and compare with CRC stored in :db under :key."""
    crc_old = db.get_key(key)
    crc_new = calc_crc(p)

    if crc_old != crc_new:
        db.set_key(key, crc_new)
        return True

    return False


def main(data_path: Path, days_to_show: int=0):
    """."""
    db = DB(str(data_path / Path("food.db")))

    if has_crc_changed(db, data_path / Path("food.yaml"), "crc_food"):
        food_yaml = load_yaml(data_path / Path("food.yaml"))
        db.insert_food(_ for _ in _yield_food_items(food_yaml))

    if has_crc_changed(db, data_path / Path("consumed.yaml"), "crc_consumed"):
        consumed_yaml = load_yaml(data_path / Path("consumed.yaml"))
        delete_insert_consumed(_yield_consumed_items(consumed_yaml), db)

    if has_crc_changed(db, data_path / Path("body.yaml"), "crc_body"):
        body_yaml = load_yaml(data_path / Path("body.yaml"))
        delete_insert_bodies(_yield_body_items(body_yaml), db)

    dates_to_show = [_ for _ in dates_till_next_sunday(days_to_show)]

    print_consumed(db, dates_to_show)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Second argument has to be the path to the config file.")
        exit()

    days_to_show = 9

    config = _config(sys.argv)
    main(config["path"], days_to_show)

    # plot_week()
