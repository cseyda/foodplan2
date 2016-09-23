"""Different scheduler to distribute meals onto different days.

Every scheduler needs an "items" list with the food to schedule.

Every scheduler can have excluded days.

2 scheduler at the moment:

- specific days:
    place meals on predetermined days.

    options:
        days: array of days to place items onto

- metric
"""

from foodplan.macros.serving import Serving
from foodplan.macros.macro import Macro

from .static import metric, specific_days

# list to keep order
schedule_plan = [
    # general night time and breakfast food
    {"scheduler": {
        "name": "specific_days",
        "options": {
            "days": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        }},
    "items": [
        {"s_type": "servings", "s_size": 1, "id": "apfel", "mt": "breakfast"},
        {"s_type": "servings", "s_size": 1, "id": "fish_oil", "mt": "breakfast"},
        [{"s_type": "servings", "s_size": 1, "id": "_Quark", "mt": "night"},
        {"s_type": "gr", "s_size": 25, "id": "haferflocken", "mt": "night"}]]
    },

    # fisch oil after training
    {"scheduler": {
        "name": "specific_days",
        "options": {
            "days": ["Di", "Do", "Sa"]}
        },
    "items": [
        {"s_type": "servings", "s_size": 1, "id": "fish_oil", "mt": "lunch"}]
    },

    # breakfast quark + outs on day with lowest protein
    {"scheduler": {
        "name": "metric",
        "options": {
            "job_name": "quark",
            "where": "low_p"}
        },
    "items": [
        [{"s_type": "servings", "s_size": 1, "id": "_Quark", "mt": "breakfast"},
        {"s_type": "gr", "s_size": 25, "id": "haferflocken", "mt": "breakfast"}]
    ]
    },

    # 2 knäckebrot + egg on 2 highest carb days
    {"scheduler": {
        "name": "metric",
        "options": {
            "job_name": "knäcke",
            "where": "high_k",
            "exclude": ["quark"]}
        },
    "items": [
        [{"s_type": "servings", "s_size": 2, "id": "knäckebrot", "mt": "breakfast"},
        {"s_type": "servings", "s_size": 1, "id": "ei", "mt": "breakfast"}],
        [{"s_type": "servings", "s_size": 2, "id": "knäckebrot", "mt": "breakfast"},
        {"s_type": "servings", "s_size": 1, "id": "ei", "mt": "breakfast"}]
    ]
    },

    # bread on the remaining 4 days
    {"scheduler": {
        "name": "specific_days",
        "options": {
            "job_name": "brot",
            "exclude": ["quark", "knäcke"]}
        },
    "items": [
        {"s_type": "servings", "s_size": 2, "id": "_Brot", "mt": "breakfast"}
        ]
    },

    # breakfast toppings
    # {"scheduler": {
    #     "name": "metric",
    #     "options": {
    #         "exclude": ["quark"]}
    #     },
    # "items": [
    #     {"s_type": "gr", "s_size": 15, "id": "honig", "mt": "breakfast"},
    #     {"s_type": "gr", "s_size": 15, "id": "marmelade", "mt": "breakfast"},
    #     {"s_type": "servings", "s_size": 1, "id": "kochschinken", "mt": "breakfast"},
    #     [{"s_type": "servings", "s_size": 1, "id": "emmentaler_aggenstein", "mt": "breakfast"},
    #      {"s_type": "servings", "s_size": 2, "id": "salami", "mt": "breakfast"}],
    #     {"s_type": "gr", "s_size": 15, "id": "cashew_mus", "mt": "breakfast"},
    #     {"s_type": "gr", "s_size": 15, "id": "mandeln", "mt": "breakfast"},
    # ]
    # },

    # breakfast toppings
    {"scheduler": {
        "name": "metric",
        "options": {
            "exclude": ["quark"],
            "rounds": 2}
        },
    "items": [
        {"s_type": "gr", "s_size": 15, "id": "honig", "mt": "breakfast"},
        {"s_type": "gr", "s_size": 15, "id": "marmelade", "mt": "breakfast"},
        {"s_type": "servings", "s_size": 1, "id": "kochschinken", "mt": "breakfast"},
        [{"s_type": "servings", "s_size": 1, "id": "emmentaler_aggenstein", "mt": "breakfast"},
         {"s_type": "servings", "s_size": 2, "id": "salami", "mt": "breakfast"}],
        {"s_type": "gr", "s_size": 15, "id": "cashew_mus", "mt": "breakfast"},
        {"s_type": "gr", "s_size": 15, "id": "mandeln", "mt": "breakfast"},
    ]
    },

    # protein shakes on days with lowest protein
    {"scheduler": {
        "name": "metric",
        "options": {
            "where": "low_p"}
        },
    "items": [
        {"s_type": "servings", "s_size": 1, "id": "vegan_blend_schoko", "mt": "lunch"},
        {"s_type": "servings", "s_size": 1, "id": "vegan_blend_schoko", "mt": "lunch"}
    ]
    }
]


class ScheduleItem(object):
    """."""

    def __init__(self, item, food_db, meal_choices):
        """."""
        self.macro = Macro(serving_size=0)

        # to keep label + serving. list for food + groups
        # meals = [(label, serving, meal_time), ...]
        self.meals = []

        self._process(item, food_db, meal_choices)

    def _process(self, item, food_db, meal_choices):
        """."""
        # normal entry
        if isinstance(item, dict):
            item_macro, label_serving_mt = self._item_macro_meta(
                item, food_db, meal_choices)

            self.meals.append(label_serving_mt)
            self.macro = item_macro
        # combined entries
        else:
            for i in item:
                tmp_macro, label_serving_mt = self._item_macro_meta(
                    i, food_db, meal_choices)

                self.meals.append(label_serving_mt)
                self.macro += tmp_macro

    def _item_macro_meta(self, item, food_db, meal_choices):
        """."""
        label = item["id"]

        if label[0] == "_":
            label = meal_choices[label[1:]]

        macro = food_db[label]
        serving = Serving(item["s_size"], item["s_type"])

        macro.set_serving(serving)

        return macro, (label, serving, item["mt"])

def prepare_schedule_food(schedule_plan, food_db, meal_choices):
    """."""
    processed_plans = []

    for plan in schedule_plan:
        processed_entries = []

        for item in plan["items"]:
            # item_macro, meta_food = _process_item(item, food_db, meal_choices)
            schedule_item = ScheduleItem(item, food_db, meal_choices)

            processed_entries.append(schedule_item)

        processed_plans.append(processed_entries)

    return processed_plans


class FoodScheduler(object):
    """."""

    def __init__(self, food, meal_choices, body_status):
        """."""
        self.body_status = body_status
        self.prepared_schedule = prepare_schedule_food(
            schedule_plan, food, meal_choices)

        self.possible_schedulers = {
            "specific_days": specific_days,
            "metric": metric}

    def schedule(self, macro_per_day, food_on_days):
        """."""
        self.exclude_names = {}

        for plan_count, schedule in enumerate(schedule_plan):
            schedule_result, macros = self.run_scheduler(
                schedule["scheduler"],
                schedule["items"],
                macro_per_day,
                self.prepared_schedule[plan_count])

            for day, mts in schedule_result.items():
                for mt, meals in mts.items():
                    for meal in meals:
                        label, serving = meal

                        food_on_days[day][mt].append((label, serving))
                        macro_per_day[day] += macros[day]

    def run_scheduler(self, options, items, macro_per_day, prepared_schedule):
        """."""
        try:
            scheduler = self.possible_schedulers[options["name"]]
        except:
            raise NotImplemented

        # remove excluded days
        days = self._remove_excluded_days(options["options"])

        s = scheduler(options["options"], days)
        schedule_result, macros, affected_days = s(
            macro_per_day, prepared_schedule)

        if "job_name" in options["options"]:
            self.exclude_names[options["options"]["job_name"]] = affected_days

        return schedule_result, macros

    def _remove_excluded_days(self, options):
        """."""
        excluded_days = set()

        if "exclude" in options:
            for ex in options["exclude"]:
                excluded_days.update(d for d in self.exclude_names[ex])

        if "days" in options:
            days = options["days"]
        else:
            days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        days = [d for d in days if d not in excluded_days]

        return days

    def output(self, days, food_on_days):
        """."""
        for day in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
            print(days[day].date.strftime("%Y%m%d:"))
            for mt in ["breakfast", "dinner", "lunch", "night"]:
                print("    - {}:".format(mt))
                comb = {}

                for meal, serving in food_on_days[day][mt]:
                    if serving.size > 0:
                        if meal in comb:
                            # gr vs servings
                            if serving.kind.name in comb[meal]:
                                comb[meal][serving.kind.name] += serving.size
                            else:
                                print("gr vs servings", comb[meal], serving)
                                comb[meal][serving.kind.name] = serving.size
                        else:
                            comb[meal] = {serving.kind.name: serving.size}

                for meal, serving in comb.items():
                    print("        {}:".format(meal))
                    if "gr" in serving:
                        print("            {}: {}".format("gr", serving["gr"]))
                    elif serving["servings"] != 1:
                        print("            {}: {}".format(
                            "servings", serving["servings"]))
