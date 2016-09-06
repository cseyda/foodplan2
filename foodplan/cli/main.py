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

def sumzip(*items):
    """."""
    return [sum(values) for values in zip(*items)]

def plot_week():
    """."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy as np

    import datetime

    from foodplan.macros.macro import Macro

    food = pickled_load_food(
        data_path / Path("food.yaml"),
        data_path / Path("crc.pickle"),
        data_path / Path("food.pickle"))

    food_consumed = pickled_load_consumed(
        data_path / Path("consumed.yaml"),
        food,
        data_path / Path("crc.pickle"),
        data_path / Path("consumed.pickle"))

    body = load_body(load_yaml(data_path / Path("body.yaml")))

    weekly = {}

    for date, m in food_consumed.items():
        date = str(date)
        year, week, day = datetime.date(
            int(date[:4]), int(date[4:6]), int(date[6:8])).isocalendar()

        if year not in weekly:
            weekly[year] = {}

        if week not in weekly[year]:
            weekly[year][week] = {"macros": [], "weight": []}

        weekly[year][week]["macros"].append(m)

    for date, w in body.items():
        date = str(date)
        year, week, day = datetime.date(
            int(date[:4]), int(date[4:6]), int(date[6:8])).isocalendar()

        if year not in weekly:
            weekly[year] = {}

        if week not in weekly[year]:
            weekly[year][week] = {"macros": [], "weight": []}

        weekly[year][week]["weight"].append(w)

    f = []
    p = []
    k = []
    weights = []

    years = sorted([y for y in weekly])
    for year in years:
        weeks = sorted([w for w in weekly[year]])

        for week in weeks:
            m = weekly[year][week]["macros"]

            week_sum = Macro(serving_size=0)

            for l in m:
                week_sum += l
            if len(m) == 0:
                continue
            # print(year, week, len(m), week_sum.kcals / len(m))
            f.append(9 * week_sum.f / len(m))
            p.append(4 * week_sum.p / len(m))
            k.append(4 * week_sum.k / len(m))

            w = weekly[year][week]["weight"]
            w_week = 0
            for l in w:
                w_week += l["w"]
            weights.append(w_week / len(w))

    ind = np.arange(len(f))

    fig, ax = plt.subplots()

    width=1
    plt.bar(ind, f, width=width, color='r')
    plt.bar(ind, p, width=width, color='b', bottom=sumzip(f))
    plt.bar(ind, k, width=width, color='g', bottom=sumzip(f, p))

    ax_w = ax.twinx()
    ax_w.plot(weights, color='black', linewidth=3)
    ax_w.grid(True)

    plt.show()

if __name__ == '__main__':
    p = "/home/seydanator/Documents/foodplan"
    days_to_show = 9

    data_path = _config(p)
    main(data_path, days_to_show)

    # plot_week()
