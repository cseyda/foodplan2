"""Static Scheduler."""

# from foodplan.macros.serving import Serving
from foodplan.macros.macro import Macro

import heapq
# from itertools import combinations


class Scheduler(object):
    """."""

    def __init__(self, options, days):
        """."""
        self.plan = {
            day: {
                mt: [] for mt in ["breakfast", "dinner", "lunch", "night"]
            } for day in days}
        self.macros = {day: Macro(serving_size=0) for day in days}


class specific_days(Scheduler):
    """."""

    def __call__(self, macro_per_day, prepared_schedule):
        """static."""
        d_set = set()

        for schedule_item in prepared_schedule:
            for day in self.plan:
                self.macros[day] += schedule_item.macro
                d_set.add(day)

                for meal in schedule_item.meals:
                    label, serving, mt = meal
                    self.plan[day][mt].append((label, serving))

        return self.plan, self.macros, d_set


class metric(Scheduler):
    """."""

    def __init__(self, options, days):
        """."""
        super().__init__(options, days)

        self.possible_modifiers = {
            # protein
            "high_p": {"f": 0, "p": 1, "k": 0},
            "low_p": {"f": 0, "p": -1, "k": 0},
            # carbs
            "high_k": {"f": 0, "p": 0, "k": 1},
            "low_k": {"f": 0, "p": 0, "k": -1},
            # fat
            "high_f": {"f": 1, "p": 0, "k": 0},
            "low_f": {"f": -1, "p": 0, "k": 0}}

        self.day_target = {"f": 60, "p": 150, "k": 200}
        self.item_pairs = []

        try:
            self.modifier = self.possible_modifiers[options["where"]]
        except KeyError:
            self.modifier = {"f": -1, "p": -1, "k": -1}

        try:
            self.rounds = options["rounds"]
        except KeyError:
            self.rounds = 1
        self.placed_on = {day: set() for day in days}

    def build_heap(self, schedule_items, macro_per_day):
        """Push score + day and item index onto max heap. Return the heap."""
        h = []

        for item_idx, schedule_item in enumerate(schedule_items):
            for day in self.plan:
                if item_idx not in self.placed_on[day]:
                    score = self.score(
                        schedule_item.macro, macro_per_day[day])
                    heapq.heappush(h, (score, day, item_idx))
        return h

    def _place_item_on_day(self, schedule_item, day):
        """."""
        for meal in schedule_item.meals:
            label, serving, mt = meal
            self.plan[day][mt].append((label, serving))
        self.macros[day] += schedule_item.macro

    def schedule_items(self, prepared_schedule, h):
        """."""
        items = set()
        days = set()

        schedule_round = {}

        for i in range(len(h)):
            score, day, item_idx = heapq.heappop(h)

            if item_idx not in items and day not in days:
                items.add(item_idx)
                days.add(day)
                print("{} -> {}".format(item_idx, day))
                schedule_round[day] = item_idx

            if len(items) == len(prepared_schedule):
                break

        for day, item_idx in schedule_round.items():
            self.placed_on[day].add(item_idx)

            schedule_item = prepared_schedule[item_idx]
            self._place_item_on_day(schedule_item, day)

        print(len(items), len(days))
        return days

    def __call__(self, macro_per_day, prepared_schedule):
        """."""
        print()
        affected_days = set()
        for _ in range(self.rounds):
            h = self.build_heap(prepared_schedule, macro_per_day)
            days = self.schedule_items(prepared_schedule, h)
            affected_days.update(days)

        return self.plan, self.macros, affected_days

    def score(self, macro, day_now):
        """."""
        s = 0
        for m in "fpk":
            day_rel = self.day_target[m] - getattr(day_now, m)
            day_rel /= self.day_target[m]
            s += day_rel * getattr(macro, m) * self.modifier[m]
        return s


def test():
    """."""
    class ScheduleItemMock():
        """."""

        def __init__(self, label, macro={"f": 0, "p": 0, "k": 0}):
            """."""
            # self.meals is not important here, label to identify
            serving = "gr"
            meal_time = "breakfast"

            self.meals = [(label, serving, meal_time)]
            self.macro = macro

    options = {"where": None}
    days = ["Mo", "Di"]

    m = metric(options, days)

    macro_per_day = {
        "Mo": Macro(f=10, p=0, k=0),
        "Di": Macro(f=0, p=10, k=0)}

    prepared_schedule = [
        ScheduleItemMock("A", Macro(f=10, p=0, k=0)),
        ScheduleItemMock("B", Macro(f=10, p=10, k=0)),
        ScheduleItemMock("C", Macro(f=10, p=0, k=10)),
        ScheduleItemMock("D", Macro(f=0, p=10, k=0))]

    schedule = m(macro_per_day, prepared_schedule)[0]

    for day, mts in schedule.items():
        print(day)

        for mt, meals in mts.items():
            if meals:
                print("  ", mt, meals)
        print()


if __name__ == '__main__':
    """."""
    test()
