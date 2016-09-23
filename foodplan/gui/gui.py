"""."""

from tkinter import ttk
import tkinter as tk

from datetime import date, datetime, timedelta
from pathlib import Path

from foodplan.input.input import pickled_load_consumed, load_body, pickled_load_food, load_yaml
from foodplan.macros.serving import Serving
from foodplan.macros.macro import Macro

from .scheduler.scheduler import FoodScheduler


class Spinbox(ttk.Widget):
    """."""

    def __init__(self, master, **kw):
        """."""
        ttk.Widget.__init__(self, master, 'ttk::spinbox', kw)

data_path = Path("/home/seydanator/Documents/foodplan")
food = pickled_load_food(
    data_path / Path("food.yaml"),
    data_path / Path("crc.pickle"),
    data_path / Path("food.pickle"))


meals = {
    "Pizza": {
        "dinner": {
            "Texmex": {
                "s_type": "servings",
                "s_size": 1,
                "id": "pizza_tex_mex"},
            "Thunfisch": {
                "s_type": "servings",
                "s_size": 1,
                "id": "thunfisch"}
        }
    },
    "Fleischkäse": {
        "dinner": {
            "Fleischkäse": {
                "s_type": "gr",
                "s_size": 200,
                "id": "fleischkäse_pizza"},
            "Kartoffeln": {
                "s_type": "gr",
                "s_size": 600,
                "id": "kartoffel"}
        }
    },
    "Brathähnchen": {
        "dinner": {
            "Hähnchen": {
                "s_type": "gr",
                "s_size": 650,
                "id": "brathähnchen_knochen"},
            "Brot": {
                "s_type": "servings",
                "s_size": 1,
                "id": "_Brot"}
        }
    },
    "Hamburger": {
        "dinner": {
            "Hamburger": {
                "s_type": "servings",
                "s_size": 3,
                "id": "Hamburger"}},
        "lunch": {
            "Mehrkornbrötchen": {
                "s_type": "servings",
                "s_size": 1,
                "id": "mehrkorn_toast_brötchen"},
            "Ei": {
                "s_type": "servings",
                "s_size": 1,
                "id": "ei"},
            "Kochschinken": {
                "s_type": "servings",
                "s_size": 1,
                "id": "kochschinken"}
        }
    },
    "Grillen": {
        "dinner": {
            "Pute": {
                "s_type": "gr",
                "s_size": 400,
                "id": "pute"},
            "Feuerwurst_werst": {
                "s_type": "servings",
                "s_size": 2,
                "id": "feuerwurst_werst"},
            "Cevapcici": {
                "s_type": "gr",
                "s_size": 280,
                "id": "cevapcici"},
            "Kartoffeln": {
                "s_type": "gr",
                "s_size": 600,
                "id": "kartoffel"},
            "Linsen": {
                "s_type": "servings",
                "s_size": 1,
                "id": "linsen_suppengrün"},
            "Erbsen Möhren": {
                "s_type": "servings",
                "s_size": 1,
                "id": "erbsen_möhren_ja"
            }
        }
    },
    "Eier": {
        "dinner": {
            "Eier25": {
                "s_type": "servings",
                "s_size": 1,
                "id": "Eier25"},
            "Brot": {
                "s_type": "servings",
                "s_size": 2,
                "id": "_Brot"},
            "Spinat": {
                "s_type": "servings",
                "s_size": 3,
                "id": "spinat_gehackt_rewe"},
            "Erbsen": {
                "s_type": "gr",
                "s_size": 25,
                "id": "erbsen_ja"},
            "Reis": {
                "s_type": "servings",
                "s_size": 0,
                "id": "rice_white"}}
    },
    "Spaghetti Bolognese": {
        "dinner": {
            "Spaghetti": {
                "s_type": "gr",
                "s_size": 300,
                "id": "nudeln_gekocht"},
            "Bolognese": {
                "s_type": "gr",
                "s_size": 200,
                "id": "hackfleisch"}},
    },
    "Fisch": {
        "dinner": {
            "Fischfilet": {
                "s_type": "servings",
                "s_size": 3,
                "id": "fischfilet_ja"},
            "Reis": {
                "s_type": "servings",
                "s_size": 1,
                "id": "rice_white"},
            "Linsen": {
                "s_type": "servings",
                "s_size": 1,
                "id": "linsen_suppengrün"},
            "Kartoffeln": {
                "s_type": "gr",
                "s_size": 600,
                "id": "kartoffel"}
        }
    },
    "Pute": {
        "dinner": {
            "Pute": {
                "s_type": "gr",
                "s_size": 400,
                "id": "pute"},
            "Reis": {
                "s_type": "servings",
                "s_size": 1,
                "id": "rice_white"},
            "Linsen": {
                "s_type": "servings",
                "s_size": 1,
                "id": "linsen_suppengrün"},
            "Erbsen Möhren": {
                "s_type": "servings",
                "s_size": 1,
                "id": "erbsen_möhren_ja"
            }
        }
    },
    "Haferflocken": {
        "dinner": {
            "Reis": {
                "s_type": "servings",
                "s_size": 1,
                "id": "rice_white"},
            "Thunfisch": {
                "s_type": "servings",
                "s_size": 1,
                "id": "thunfisch"}
        },
        "lunch": {
            "Haferflocken": {
                "s_type": "gr",
                "s_size": 100,
                "id": "haferflocken"}
        }
    },
    "Putenschnitzel": {
        "dinner": {
            "Schnitzel": {
                "s_type": "gr",
                "s_size": 450,
                "id": "Putenschnitzel"},
            "Nudeln": {
                "s_type": "gr",
                "s_size": 350,
                "id": "nudeln_gekocht"},
            "Reis": {
                "s_type": "gr",
                "s_size": 450,
                "id": "rice_cooked"},
            "Kartoffelbrei": {
                "s_type": "gr",
                "s_size": 400,
                "id": "kartoffelbrei"},
            "Kartoffeln": {
                "s_type": "gr",
                "s_size": 600,
                "id": "kartoffel"},
            "Erbsen + Möhren": {
                "s_type": "servings",
                "s_size": 1,
                "id": "erbsen_möhren_ja"}
        }
    },

    "Geschnetzeltes": {
        "dinner": {
            "Fleisch": {
                "s_type": "gr",
                "s_size": 400,
                "id": "pute"},
            "Nudeln": {
                "s_type": "gr",
                "s_size": 350,
                "id": "nudeln_gekocht"},
            "Reis": {
                "s_type": "gr",
                "s_size": 400,
                "id": "rice_cooked"},
        }
    }
}

meal_options = {
    "Quark": {
        "Leinöl": {"id": "QuarkEi2"},
        "Wallnuss": {"id": "QuarkWallnuss"},
        "Mandel": {"id": "QuarkMandel"},
        "Avocado": {"id": "QuarkAvo"}
    },
    "Brot": {
        "Malzmehrkorn": {"id": "malz_mehrkornbrot"},
        "Balance": {"id": "balance_brot"}
    }
}
# breakfast_options = {"p"}


class LunchtimeFrame(ttk.LabelFrame):
    """."""

    def __init__(self, master, label):
        """Init. Label + text + create other widgets."""
        super().__init__(master=master, text=label)

        self.label = label
        self.meals = []

    def fill_meal_frames(self, row, meal, s_type, s_size, m_id):
        """."""
        ll = ttk.Label(self, text=meal)

        size_var = tk.StringVar()
        size_var.set(s_size)
        spin_size = tk.Spinbox(
            self, textvariable=size_var,
            from_=0, to=99999, increment=.1, width=4)

        oo_var = tk.StringVar()
        oo = ttk.OptionMenu(
            self, oo_var,
            *["gr", "gr", "servings"])  # , command=handler)
        oo_var.set(s_type)

        ll.grid(row=row*2, column=0, columnspan=2)
        spin_size.grid(row=row*2+1, column=0)
        oo.grid(row=row*2+1, column=1, sticky=tk.W+tk.E)

        self.meals.append((m_id, size_var, oo_var))

    def clear(self):
        """Remove meal options from time frames."""
        self.meals.clear()

        for child in self.winfo_children():
            child.destroy()

    def getMacros(self, meal_choices):
        """."""
        macro = Macro(serving_size=0)
        m = []
        for label, s_size, s_type in self.meals:
            serving_size = float(s_size.get())
            serving_kind = str(s_type.get())
            # print(label, serving_size, serving_kind)

            if label[0] == "_":
                label = meal_choices[label[1:]]

            f = food[label]
            serving = Serving(serving_size, serving_kind)
            f.set_serving(serving)
            # print(food[label])
            m.append((label, serving))
            macro += f
        return macro, m


class DayFrame(ttk.LabelFrame):
    """."""

    def __init__(self, master, label, date):
        """Init. Label + text + create other widgets."""
        self.date = date
        self.label = label

        self.label_format = "{} {:02}.{:02}."

        super().__init__(
            master=master,
            text=self.label_format.format(label, date.day, date.month))

        self.meal_times = {}
        self.create_widgets(label)

    def update_date(self, date):
        """Update the date in frames label."""
        self.date = date
        self["text"] = self.label_format.format(
            self.label, date.day, date.month)

    def create_widgets(self, label):
        """Dropdown with meals. Frames for dinner + lunch."""
        # list with meal options, first is empty
        optList = [' ']
        optList += list(meals)

        # v holds the choice
        v = tk.StringVar()
        self.option = v

        def handler(event, self=self, ident=label):
            return self.on_combo_selected(event, ident)

        o = ttk.OptionMenu(self, v, *optList, command=handler)
        # o = ttk.OptionMenu(fr, v, *optList, command=handler)
        o.grid(sticky=tk.E+tk.W)
        # o.columnconfigure(0, weight=1)

        for row, meal_time in enumerate(["dinner", "lunch"], 1):
            mt = LunchtimeFrame(self, meal_time)
            mt.grid(row=row, sticky=tk.E+tk.W)

            self.meal_times[meal_time] = mt

    def on_combo_selected(self, event, ident):
        """Combobox for foods. On change delete previously entried foods and enter new ones."""
        # print("event", event, "ident", ident)
        for mt in ["dinner", "lunch"]:
            mt_frame = self.meal_times[mt]
            mt_frame.clear()

            for row, meal in enumerate(meals[event].get(mt, [])):
                s_type = meals[event][mt][meal]["s_type"]
                s_size = meals[event][mt][meal]["s_size"]
                m_id = meals[event][mt][meal]["id"]

                mt_frame.fill_meal_frames(
                    row, meal, s_type, s_size, m_id)

    def getMacros(self, meal_choices):
        """."""
        m = {"dinner": [], "lunch": [], "breakfast": [], "night": []}
        macros_day = Macro(serving_size=0)

        for mt in ["dinner", "lunch"]:
            mt_frame = self.meal_times[mt]

            macro, mt_m = mt_frame.getMacros(meal_choices)
            macros_day += macro

            m[mt].extend(mt_m)
        return macros_day, m

class Application(ttk.Frame):
    """Mainframe."""

    def __init__(self, master=None):
        """."""
        super().__init__(master)

        self.master = master
        self.grid()

        self.today = date.today()

        # holds the StingVar for the different foods of the week
        self.opt_var = {}

        # holds the DayFrames
        self.days = {}
        self.create_widgets()

    def schedule_food(self, macro_per_day, food_on_days):
        """."""
        from foodplan.input.output import _get_bodystatus

        body_yaml = load_yaml(data_path / Path("body.yaml"))
        body = load_body(body_yaml)
        body_dates = sorted([int(d) for d in body])
        body_status = body[_get_bodystatus(
            body_dates, self.today.strftime("%Y%m%d"))]

        scheduler = FoodScheduler(food, self.meal_choices, body_status)
        scheduler.schedule(macro_per_day, food_on_days)
        scheduler.output(self.days, food_on_days)

    def on_button_press(self):
        """."""
        macro_per_day = {}
        food_on_days = {}

        self.meal_choices = {}
        for k, v in self.opt_var.items():
            self.meal_choices[k] = meal_options[k][v.get()]["id"]

        for day in ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]:
            macros_day, m = self.days[day].getMacros(self.meal_choices)
            food_on_days[day] = m
            macro_per_day[day] = macros_day
        self.schedule_food(macro_per_day, food_on_days)

    def on_change_week(self, var):
        """."""
        week_number = int(var.get())
        today_week = self.today.isocalendar()[1]
        diff_week = week_number - today_week

        week = self.today + timedelta(7*diff_week)

        week_year, week_week, week_day = week.isocalendar()

        # get date of first day in week
        week_monday = datetime.strptime(
            "{}-W{}-1".format(week_year, week_week), "%Y-W%W-%w")

        for c, day in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]):
            date = week_monday + timedelta(c)
            self.days[day].update_date(date)

    def create_widgets(self):
        """Create options frame + frames for the different days."""
        optionFrame = ttk.LabelFrame(self, text="Options")
        optionFrame.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)

        row = 0

        nextweek_monday = self.create_week_spin(optionFrame, row)
        row += 1

        for label, opts in meal_options.items():
            self.create_food_option_dropdown(optionFrame, label, opts, row)
            row += 1

        ok_button = ttk.Button(master=optionFrame, text="OK", command=self.on_button_press)
        ok_button.grid()
        row += 1

        # create dayframes
        for col, day in enumerate(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"], 1):
            df = DayFrame(self, day, date=nextweek_monday + timedelta(col - 1))
            df.grid(column=col, row=0, sticky=tk.N+tk.S+tk.E+tk.W)

            self.days[day] = df

    def create_food_option_dropdown(self, master, label, opts, row):
        """."""
        options = list(opts)
        options.append(options[0])

        droplabel = ttk.Label(master=master, text=label)

        self.opt_var[label] = tk.StringVar()
        dropmenu = ttk.OptionMenu(
            master, self.opt_var[label],
            *options)  # , command=handler)
        # quark_var.set(list(quark)[0])

        droplabel.grid(row=row, column=0)
        dropmenu.grid(row=row, column=1)

    def create_week_spin(self, master, row):
        """."""
        week_label = ttk.Label(master=master, text="Week")
        # set week
        # usually planning one week ahead, so we take
        # because of year and month limits, only use date objects + timedelta

        # wd = self.today.weekday()
        # td = timedelta(7-wd % 7)
        # start_date = self.today + td

        # get to next week
        nextweek = self.today + timedelta(7)
        nextweek_year, nextweek_week, nextweek_day = nextweek.isocalendar()

        # get date of first day in week
        nextweek_monday = datetime.strptime(
            "{}-W{}-1".format(nextweek_year, nextweek_week), "%Y-W%W-%w")

        week_var = tk.StringVar()
        week_var.set(nextweek_week)

        week_spin = tk.Spinbox(
            master, textvariable=week_var,
            from_=1, to=53, increment=1, width=2)

        week_label.grid(column=0, row=row)
        week_spin.grid(column=1, row=row)

        def week_handler(var, ka, event, variable=week_var, self=self):
            return self.on_change_week(variable)
        week_var.trace("w", callback=week_handler)

        return nextweek_monday


def main():
    """."""
    root = tk.Tk()
    app = Application(master=root)
    app.master.title('Schedule Food')
    app.mainloop()

if __name__ == '__main__':
    main()
