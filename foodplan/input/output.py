"""."""

from collections import defaultdict
import datetime

from foodplan.macros.macro import Macro
from foodplan.macros.body import Body

from foodplan.db.db import macros_from_consumed


class bcolors:
    """Colors."""

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


template_header = "{}{:^8}{:^5}{:^4}{:^4}{:^4}{}".format(
    bcolors.UNDERLINE + bcolors.OKGREEN,
    "date", "kcals", " f", " p", " c", bcolors.ENDC)
template_dates = "".join([
    "{line}{date:^8}{col_kcals}{kcals:5.0f}{endc}",
    "{line}{col_f}{f:4.0f}{endc}",
    "{line}{col_p}{p:4.0f}{endc}",
    "{line}{col_k}{k:4.0f}{endc}"])


def _get_colors(body_status, macros):
    """."""
    col = defaultdict(str)
    colors = [bcolors.WARNING, "", bcolors.OKBLUE, bcolors.FAIL]

    for macro in ["f", "p", "k", "kcals"]:
        # set colors
        m = getattr(macros, macro)

        col[macro] = colors[-1]
        for r, color in zip(body_status.limits[macro], colors):
            if m < r:
                col[macro] = color
                break

    return col


def _get_now_str(hours: int=0) -> str:
    """Return the data as string."""
    delta = datetime.timedelta(hours=hours)
    today = datetime.datetime.now() - delta
    return today.strftime("%Y%m%d")


def print_consumed(db, dates_to_show):
    """."""
    data = _generate_output_data(db, dates_to_show)
    output_str = _get_output_string(data)
    print(output_str)


def _generate_output_data(db, dates_to_show):
    """."""
    today = _get_now_str(5)
    body_today = None
    avg = Macro(serving_size=0)

    data = []
    data.append((template_header, {}))

    for day in dates_to_show:
        day = day.strftime("%Y%m%d")

        m = macros_from_consumed(db.consumed(day), db)
        avg += m

        body_status = Body.RecordFactory(db.body(day))

        col = _get_colors(body_status, m)

        if str(today) == str(day):
            col["day"] = bcolors.BOLD
            body_today = body_status

        conf = {
            "line": col["day"], "date": day,
            "col_kcals": col["kcals"], "kcals": m.kcals,
            "col_f": col["f"], "f": m.f,
            "col_p": col["p"], "p": m.p,
            "col_k": col["k"], "k": m.k,
            "endc": bcolors.ENDC}
        data.append((template_dates, conf))

    # if today is not present in consumed_dates
    if not body_today:
        day = dates_to_show[0].strftime("%Y%m%d")
        body_today = Body.RecordFactory(db.body(day))

    data.append((None, {}))

    conf = {
        "line": col["day"], "date": "average ",
        "col_kcals": "", "kcals": avg.kcals / len(dates_to_show),
        "col_f": "", "f": avg.f / len(dates_to_show),
        "col_p": "", "p": avg.p / len(dates_to_show),
        "col_k": "", "k": avg.k / len(dates_to_show),
        "endc": bcolors.ENDC}

    data.append((template_dates, conf))
    data.append((None, {}))

    min_ = defaultdict(str)
    min_.update({
        "date": "Min",
        "line": bcolors.UNDERLINE,
        "kcals": body_today.limits["kcals"][0],
        "f": body_today.limits["f"][0],
        "p": body_today.limits["p"][0],
        "k": body_today.limits["k"][0]
    })

    data.append((template_dates, min_))

    max_ = defaultdict(str)
    max_.update({
        "date": "Max",
        "kcals": body_today.limits["kcals"][1],
        "f": body_today.limits["f"][1],
        "p": body_today.limits["p"][1],
        "k": body_today.limits["k"][1]
    })

    data.append((template_dates, max_))
    return data


def _get_output_string(data):
    """."""
    output = []

    for tpl, vals in data:
        if tpl:
            output.append(tpl.format(**vals))
        output.append("\n")

    return "".join(output)
