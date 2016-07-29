"""."""

from pathlib import Path
import copy

import pickle
from collections import defaultdict

import yaml

from foodplan.macros.macro import Macro
from foodplan.macros.serving import Serving


# YAML, PICKLE

def load_yaml(yaml_path: Path) -> dict:
    """Return dict from yaml document."""
    with yaml_path.open("r") as file_open:
        yaml_dict = load_string(file_open)
    return yaml_dict


def load_string(yaml_string: str) -> dict:
    """."""
    yaml_dict = yaml.safe_load(yaml_string)
    return yaml_dict


def _pickled_load(**kwargs) -> dict:
    """in: file_path, pickle_path, load_func, load_args."""
    crc_path = kwargs["crc_path"]
    file_path = kwargs["file_path"]
    pickle_path = kwargs["pickle_path"]
    load_func = kwargs["load_func"]
    load_args = kwargs.get("load_args", {})

    file_dict = None

    with _Crc(crc_path, file_path) as crc_match:
        if crc_match:
            if pickle_path.exists():
                with pickle_path.open('rb') as f:
                    file_dict = pickle.load(f)
                    return file_dict

        file_dict = load_func(file_path, **load_args)

        with pickle_path.open('wb') as f:
            pickle.dump(file_dict, f, pickle.HIGHEST_PROTOCOL)

        return file_dict

# CRC

class _Crc(object):
    """."""

    def __init__(self, crc_file_path, file_path):
        self.crc_file_path = crc_file_path
        self.file_path = file_path

        self.crc_dict = self._load()
        self.file_crc = self.calc_crc(self.file_path)

    def __enter__(self):
        """Return if the CRC has changed."""
        return self.crc_dict[self.file_path.name] == self.file_crc

    def __exit__(self, exc_type, exc_value, traceback):
        """Update CRC at the end (so a new pickle can be written)."""
        if self.crc_dict[self.file_path.name] != self.file_crc:
            self.crc_dict.update({self.file_path.name: self.file_crc})

            with self.crc_file_path.open('wb') as f:
                pickle.dump(self.crc_dict, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def calc_crc(pathName):
        """Calculate CRC.

        https://stackoverflow.com/questions/1742866/compute-crc-of-file-in-python
        """
        import zlib

        prev = 0
        with pathName.open("rb") as f:
            for eachLine in f:
                prev = zlib.crc32(eachLine, prev)
        return "%X"%(prev & 0xFFFFFFFF)

    def _load(self):
        """Load pickled dictionary containing crc information."""
        crc_dict = defaultdict(str)

        if self.crc_file_path.exists():
            with self.crc_file_path.open('rb') as f:
                crc_dict = pickle.load(f)

        return crc_dict


# FOOD

def _parse_base(f_content):
    """."""
    serving_size = f_content.get("_serving_size", 100)

    macro = Macro(
        f=f_content.get("f", 0.0), p=f_content.get("p", 0.0),
        k=f_content.get("k", 0.0), a=f_content.get("a", 0.0),
        serving_size=serving_size)
    return macro


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


def _parse_food(yaml_food: dict):
    """Seperate incredients from recipes."""
    # base = []
    recipes = []

    food = {}

    for name, f_content in yaml_food.items():
        if "base" == f_content["_type"]:
            macro = _parse_base(f_content)
            macro.name = name

            # base.append((name, macro))
            food[name] = macro

        elif "recipe" == f_content["_type"]:
            servings, incredients = _parse_recipe(f_content)

            recipes.append((name, servings, incredients))

    for name, servings, incredients in recipes:
        r = Macro(serving_size=0)
        for incredient, serving in incredients.items():
            m = copy.copy(food[incredient])
            m.set_serving(serving)
            r = r + m
        r.name = name
        r.serving_size = r.size / servings

        food[name] = r

    return food

def get_food_from_file(food_path: Path) -> dict:
    """."""
    food_dict = load_yaml(food_path)
    food = _parse_food(food_dict)
    return food


def pickled_load_food(food_path: Path, crc_path: Path, pickle_path: Path) -> dict:
    """."""
    pickled_object = _pickled_load(
        crc_path=crc_path,
        file_path=food_path,
        pickle_path=pickle_path,
        load_func=get_food_from_file,
        load_args={})

    return pickled_object

# CONSUMED

def _parse_consumed(consumed_yaml: dict, food: dict):
    """."""
    # sort consumed_yaml, get days to do
    days = sorted((day for day in consumed_yaml), reverse=True)
    days_kcals = {}

    for day in days:
        r = Macro(serving_size=0)
        for eaten, serving in consumed_yaml[day].items():
            # in case there are temporary foods
            m = None
            meal_serving = Serving(1, "servings")

            if serving:
                for serving_kind, serving_size in serving.items():
                    if serving_kind == "macros":
                        m = Macro(
                            f=serving_size.get("f", 0),
                            p=serving_size.get("p", 0),
                            k=serving_size.get("k", 0),
                            a=serving_size.get("a", 0))
                    else:
                        meal_serving = Serving(serving_size, serving_kind)
            if not m:
                m = copy.copy(food[eaten])

            m.set_serving(meal_serving)
            r = r + m
        days_kcals[day] = r
    return days_kcals

def get_consumed_from_file(consumed_path: Path, food: dict) -> dict:
    """."""
    consumed_dict = load_yaml(consumed_path)
    consumed = _parse_consumed(consumed_dict, food)
    return consumed

def pickled_load_consumed(
        consumed_path: Path, food: dict,
        crc_path: Path, pickle_path: Path) -> dict:
    """."""
    pickled_object = _pickled_load(
        crc_path=crc_path,
        file_path=consumed_path,
        pickle_path=pickle_path,
        load_func=get_consumed_from_file,
        load_args={"food": food})

    return pickled_object

# def load_consumed(consumed_path: Path, food: dict) -> dict:
#     """."""
#     crc_path = Path("tests/resources/crc.pickle")
#     pickle_path = Path("tests/resources/consumed.pickle")
#
#     consumed = None
#     with _Crc(crc_path, consumed_path) as crc_match:
#         if crc_match:
#             with pickle_path.open('rb') as f:
#                 consumed = pickle.load(f)
#
#         else:
#             consumed = get_consumed_from_file(consumed_path, food)
#
#             with pickle_path.open('wb') as f:
#                 pickle.dump(consumed, f, pickle.HIGHEST_PROTOCOL)
#
#     return consumed


def _calc_tdee(measures):
    """."""
    w = measures["weight"]
    f = measures["bodyfat"]

    # lbm: lean body mass
    lbm = w * (100 - f) / 100

    # bmr: body maintenace rate
    #      ckals needed to just stay alive
    bmr = 370 + (21.6 * lbm)

    # aa: activity level
    al = measures.get("activity_level", 1.375)

    # tdee: total daily energy expenditure
    tdee = bmr * al

    # loosing weight: -%
    # atdee: adjusted tdee
    atdee = tdee * (100 + measures.get("tdee_adjust", 0)) / 100

    return {
        "w": w, "bodyfat": f,
        "lbm": lbm, "bmr": bmr, "al": al,
        "tdee": tdee, "atdee": atdee}


def _calc_limits(body_status) -> dict:
    """."""
    # gr per kg lean body mass
    range_multi = {"f": [0.9, 1.3],
                   "p": [2.3, 3.1],
                   "k": []}  # k basically the leftover kcals

    ranges = {"f": [], "p": [], "k": [], "kcals": []}
    for macro in "fp":
        for limit in range_multi[macro]:
            ranges[macro].append(limit * body_status["lbm"])

    ranges["k"].append(
        (body_status["atdee"]-ranges["f"][1]*9-ranges["p"][1]*4) / 4)
    ranges["k"].append(
        (body_status["atdee"]-ranges["f"][0]*9-ranges["p"][0]*4) / 4)

    ranges["kcals"] = [
        body_status["atdee"]*0.9,
        body_status["atdee"]*1.1,
        body_status["atdee"]*1.3]

    return ranges


# BODY

def load_body(body_dict: dict) -> dict:
    """Read dict from body file and return tdee and ranges."""
    body_db = {}
    for date_str, measures in body_dict.items():
        body_status = _calc_tdee(measures)
        body_status["range"] = _calc_limits(body_status)

        body_db[date_str] = body_status
    return body_db


def test():
    """."""
    test_str = """
milch_und_quark:
    _type: recipe
    _servings: 28

    milch03:
        gr: 200
    quark:
        gr: 50

# milchprodukte und ei
milch03:
    _type: base

    f: 0.0
    p: 5.
    k: 5.

quark:
    _type: base

    f:  5.
    p: 10.
    k:  0.
    """
    test_dict = load_string(test_str)
    incredients, recipes = _seperate_base_recipes(test_dict)
    print(incredients, recipes)

if __name__ == '__main__':
    test()
