"""."""

from os import sys
from pathlib import Path

import yaml

from foodplan.input.input import load_yaml, calc_crc

from foodplan.input.input import load_body, get_consumed_from_file

from foodplan.input.output import print_consumed

from foodplan.db.db import DB
from foodplan.input.input import _yield_food_items


def _config(path_str: str = None):
    """."""
    if path_str:
        data_path = Path(path_str)
    else:
        if len(sys.argv) != 2:
            print("Second argument has to be the folder with the files.")
            exit()
        data_path = Path(sys.argv[1])
    return data_path


def main(data_path: Path, days_to_show: int=0):
    """."""
    db = DB(str(data_path / Path("food.db")))

    # load food only if neccesary
    crc_food_old = db.get_key("crc_food")
    crc_food_new = calc_crc(data_path / Path("food.db"))

    if crc_food_old != crc_food_new:
        db.set_key("crc_food", crc_food_new)

        with (data_path / Path("food.yaml")).open("r") as f:
            food_yaml = yaml.safe_load(f)

        db.insert_food(_ for _ in _yield_food_items(food_yaml))

    consumed = get_consumed_from_file(
        data_path / Path("consumed.yaml"), db)

    body_yaml = load_yaml(data_path / Path("body.yaml"))
    body = load_body(body_yaml)

    print_consumed(consumed, body, days_to_show)


def sumzip(*items):
    """."""
    return [sum(values) for values in zip(*items)]


if __name__ == '__main__':
    p = "/home/seydanator/Documents/foodplan"
    days_to_show = 9

    data_path = _config(p)
    main(data_path, days_to_show)

    # plot_week()
