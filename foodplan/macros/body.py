"""."""


class Body(object):
    """."""

    def __init__(self, date, weight, bodyfat, adjust, activity_level):
        """."""
        self.d = date
        self.w = weight
        self.f = bodyfat
        self.adjust = adjust
        self.al = activity_level

        _ = self._calc_tdee()
        self.lbm, self.bmr, self.tdee, self.atdee = _

        self.limits = self._calc_limits()

    @classmethod
    def RecordFactory(cls, record):
        """."""
        return cls(*record)

    def _calc_tdee(self):
        """Calculate TDEE and surrounding numbers.

        LBM, BMR, aTDEE
        """
        # lbm: lean body mass
        lbm = self.w * (100 - self.f) / 100

        # bmr: body maintenace rate
        #      ckals needed to just stay alive
        bmr = 370 + (21.6 * lbm)

        # tdee: total daily energy expenditure
        tdee = bmr * self.al

        # loosing weight: -%
        # atdee: adjusted tdee
        atdee = tdee * (100 + self.adjust) / 100

        return lbm, bmr, tdee, atdee

    def _calc_limits(self):
        """."""
        # gr per kg lean body mass
        range_multi = {"f": [0.9, 1.3],
                       "p": [2.3, 3.1],
                       "k": []}  # k basically the leftover kcals
        limits = {"f": [], "p": [], "k": [], "kcals": []}

        for macro, ranges in range_multi.items():
            for limit in ranges:
                limits[macro].append(limit * self.lbm)

        for c in [1, 0]:
            limits["k"].append(
                (self.atdee - limits["f"][c] * 9 -
                    limits["p"][c] * 4) / 4)

        limits["kcals"] = [
            self.atdee * 0.9,
            self.atdee * 1.1,
            self.atdee * 1.3]

        return limits
