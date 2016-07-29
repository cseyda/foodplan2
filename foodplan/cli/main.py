"""."""

from os import sys
from pathlib import Path

from foodplan.input.input import load_yaml
# from foodplan.input.input import _seperate_base_recipes
from foodplan.input.input import pickled_load_consumed, load_body, pickled_load_food

from foodplan.input.output import print_consumed


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
    body_yaml = load_yaml(data_path / Path("body.yaml"))
    # food_yaml = load_yaml(data_path / Path("food.yaml"))
    # consumed_yaml = load_yaml(data_path / Path("consumed.yaml"))

    # food = _seperate_base_recipes(food_yaml)
    food = pickled_load_food(
        data_path / Path("food.yaml"),
        data_path / Path("crc.pickle"),
        data_path / Path("food.pickle"))

    food_consumed = pickled_load_consumed(
        data_path / Path("consumed.yaml"),
        food,
        data_path / Path("crc.pickle"),
        data_path / Path("consumed.pickle"))

    body = load_body(body_yaml)

    print_consumed(food_consumed, body, days_to_show)

if __name__ == '__main__':
    p = "/home/seydanator/Documents/foodplan"
    days_to_show = 8

    data_path = _config(p)
    main(data_path, days_to_show)
