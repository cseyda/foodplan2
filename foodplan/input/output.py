"""."""

from collections import defaultdict
from bisect import bisect_right
import datetime

from foodplan.macros.macro import Macro


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
    bcolors.UNDERLINE+bcolors.OKGREEN,
    "date", "kcals", " f", " p", " c", bcolors.ENDC)
template_dates = "".join([
    "{line}{date:^8}{col_kcals}{kcals:5.0f}{endc}",
    "{line}{col_f}{f:4.0f}{endc}",
    "{line}{col_p}{p:4.0f}{endc}",
    "{line}{col_k}{k:4.0f}{endc}"])


def _get_bodystatus2(bodies, day):
    """."""
    body_dates = sorted([d for d in bodies], reverse=True)

    body = None
    for b_date in body_dates:
        # print(int(b_date), int(date))
        if int(b_date) <= int(day):
            body = bodies[b_date]
            break
    if not body:
        body = bodies[body_dates[-1]]
    return body


def _get_bodystatus(bodies, day):
    """."""
    i = bisect_right(bodies, int(day))
    if i:
        return bodies[i-1]
    return bodies[0]


def _get_colors(body_status, macros):
    """."""
    col = defaultdict(str)
    colors = [bcolors.WARNING, "", bcolors.OKBLUE, bcolors.FAIL]

    for macro in ["f", "p", "k", "kcals"]:
        # set colors
        m = getattr(macros, macro)

        col[macro] = colors[-1]
        for r, color in zip(body_status["range"][macro], colors):
            if m < r:
                col[macro] = color
                break

    return col


def _get_now_str(hours: int=0) -> str:
    """Return the data as string."""
    delta = datetime.timedelta(hours=hours)
    today = datetime.datetime.now() - delta
    return today.strftime("%Y%m%d")


def print_consumed(consumed, body, days_to_show: int=0):
    """."""
    today = _get_now_str(5)
    body_today = None
    avg = Macro(serving_size=0)

    # sort body_dates
    body_dates = sorted([int(d) for d in body])
    consumed_dates = sorted([d for d in consumed], reverse=True)[:days_to_show]

    print(template_header)
    for day in consumed_dates:
        m = consumed[day]
        avg += m

        # get body_status, ranges for day
        body_status = body[_get_bodystatus(body_dates, day)]

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
        print(template_dates.format(**conf))

    print("")
    conf = {
        "line": col["day"], "date": "average ",
        "col_kcals": "", "kcals": avg.kcals / len(consumed_dates),
        "col_f": "", "f": avg.f / len(consumed_dates),
        "col_p": "", "p": avg.p / len(consumed_dates),
        "col_k": "", "k": avg.k / len(consumed_dates),
        "endc": bcolors.ENDC}
    print(template_dates.format(**conf))
    print("")

    minmax = defaultdict(str)
    minmax.update({
        "date": "Min",
        "line": bcolors.UNDERLINE,
        "kcals": body_today["range"]["kcals"][0],
        "f": body_today["range"]["f"][0],
        "p": body_today["range"]["p"][0],
        "k": body_today["range"]["k"][0]
    })
    print(template_dates.format(**minmax))

    minmax.update({
        "date": "Max",
        "kcals": body_today["range"]["kcals"][1],
        "f": body_today["range"]["f"][1],
        "p": body_today["range"]["p"][1],
        "k": body_today["range"]["k"][1]
    })
    print(template_dates.format(**minmax))


def test():
    """."""
    body = {
        "20160830": "20160830",
        "20160827": "20160827",
        "20160826": "20160826"}

    # input, expected output
    cases = (
        [20160825, 20160826], [20160826, 20160826], [20160827, 20160827],
        [20160828, 20160827], [20160829, 20160827], [20160830, 20160830],
        [20160831, 20160830])

    for inp, outp in cases:
        print(outp, inp, "->", _get_bodystatus(body, str(inp)))
        assert int(outp) == int(_get_bodystatus(body, str(inp)))

    for inp, outp in cases:
        print(outp, inp, "->", _get_bodystatus2(body, str(inp)))
        assert int(outp) == int(_get_bodystatus2(body, str(inp)))


if __name__ == '__main__':
    test()
