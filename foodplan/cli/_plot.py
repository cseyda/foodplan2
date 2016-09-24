"""Plot functionality."""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import datetime

from foodplan.macros.macro import Macro


def plot_week():
    """."""
    # TODO: fix file loading
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

    width = 1
    plt.bar(ind, f, width=width, color='r')
    plt.bar(ind, p, width=width, color='b', bottom=sumzip(f))
    plt.bar(ind, k, width=width, color='g', bottom=sumzip(f, p))

    ax_w = ax.twinx()
    ax_w.plot(weights, color='black', linewidth=3)
    ax_w.grid(True)

    plt.show()


def sumzip(*items):
    """."""
    return [sum(values) for values in zip(*items)]
