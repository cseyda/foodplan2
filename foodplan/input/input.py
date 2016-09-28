"""."""

from pathlib import Path
import copy

import yaml

from foodplan.macros.macro import Macro
from foodplan.macros.serving import Serving

from foodplan.db.db import ConsumedRecord, BodyRecord


# YAML

def load_yaml(yaml_path: Path) -> dict:
    """Return dict from yaml document."""
    with yaml_path.open("r") as file_open:
        yaml_dict = load_string(file_open)
    return yaml_dict


def load_string(yaml_string: str) -> dict:
    """."""
    yaml_dict = yaml.safe_load(yaml_string)
    return yaml_dict


# CRC
def calc_crc(pathName):
    """Calculate CRC.

    https://stackoverflow.com/questions/1742866/compute-crc-of-file-in-python
    """
    import zlib

    prev = 0
    with pathName.open("rb") as f:
        for eachLine in f:
            prev = zlib.crc32(eachLine, prev)
    return "%X" % (prev & 0xFFFFFFFF)


# FOOD
def _parse_recipe(f_content):
    """."""
    servings = f_content.get("_servings", None)
    if servings:
        del f_content["_servings"]
    else:
        servings = 1

    incredients = {}
    for incredient, serving in f_content.items():
        if incredient[0] == "_":  # _type, _preperation
            continue

        if serving:
            for serving_kind, serving_size in serving.items():
                incredients[incredient] = Serving(serving_size, serving_kind)
        else:
            incredients[incredient] = Serving(1, "servings")

    return servings, incredients


def _yield_food_items(yaml_food: dict):
    """."""
    recipes = []

    for name, f_content in yaml_food.items():
        if "base" == f_content["_type"]:
            serving_size = f_content.get("_serving_size", 100)

            f = f_content.get("f", 0.0)
            p = f_content.get("p", 0.0)
            k = f_content.get("k", 0.0)
            a = f_content.get("a", 0.0)

            yield ("base", (name, f, p, k, a, serving_size))
        elif "recipe" == f_content["_type"]:
            servings, incredients = _parse_recipe(f_content)
            recipes.append((name, servings, incredients))

    yield from (("recipe", recipe) for recipe in recipes)


def _parse_food(yaml_food: dict):
    """Seperate incredients from recipes."""
    # base = []

    food = {}

    for food_item in _yield_food_items(yaml_food):
        if food_item[0] == "base":
            name, f, p, k, a, serving_size = food_item[1]

            macro = Macro(f=f, p=p, k=k, a=a, serving_size=serving_size)
            macro.name = name

            food[name] = macro

        elif food_item[0] == "recipe":
            name, servings, incredients = food_item[1]
            r = Macro(serving_size=0)
            for incredient, serving in incredients.items():
                m = copy.copy(food[incredient])
                m.set_serving(serving)
                r = r + m
            r.name = name
            r.serving_size = r.size / servings

            food[name] = r
        else:
            raise NotImplemented(
                "Itemtype {} in parser not implemented" % food_item[0])

    return food


def get_food_from_file(food_path: Path) -> dict:
    """."""
    food_dict = load_yaml(food_path)
    food = _parse_food(food_dict)
    return food


# CONSUMED
def _parse_item(food_time_obj):
    """."""
    for food_time, foods in food_time_obj.items():
        if foods:
            for food, serving in foods.items():
                s_type, s_size = _parse_serving(serving)
                yield food, food_time, s_type, s_size


def _parse_serving(serving):
    """."""
    s_size = 1
    s_type = "servings"

    if serving:
        for s_t in serving:
            s_size = serving[s_t]
            s_type = s_t
    return s_type, s_size


def _yield_consumed_items(consumed_yaml):
    """."""
    for date, food_times in consumed_yaml.items():
        for food_time_obj in food_times:
            if isinstance(food_time_obj, str):
                serving = food_times[food_time_obj]
                s_type, s_size = _parse_serving(serving)
                food = food_time_obj
                food_time = ""

                yield ConsumedRecord(date, food, food_time, s_type, s_size)

            else:
                for _ in _parse_item(food_time_obj):
                    food, food_time, s_type, s_size = _

                    yield ConsumedRecord(date, food, food_time, s_type, s_size)


def _parse_consumed(consumed_yaml: dict, food_db: dict):
    """."""
    days_kcals = {}
    for _ in _yield_consumed_items(consumed_yaml):
        date, food, food_time, s_type, s_size = _

        # if date not in days_kcals:
        #    days_kcals[date] = Macro(serving_size=0)

        m = food_db[food]
        m.set_serving(Serving(s_size, s_type))

        try:
            days_kcals[date] += m
        except KeyError:
            days_kcals[date] = m

    return days_kcals


def get_consumed_from_file(consumed_path: Path, food: dict) -> dict:
    """."""
    consumed_dict = load_yaml(consumed_path)
    consumed = _parse_consumed(consumed_dict, food)
    return consumed

# BODY


def _yield_body_items(body_dict: dict):
    """."""
    for date_str, measures in body_dict.items():
        w = measures["weight"]
        f = measures["bodyfat"]

        tdee_adjust = measures.get("tdee_adjust", 0)
        al = measures.get("activity_level", 1.375)

        yield BodyRecord(date_str, w, f, tdee_adjust, al)
