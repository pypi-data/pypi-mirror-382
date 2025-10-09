from orient_ficc_pricer.base_function.base_pricer import *


class Binary(BasePricer):

    def __init__(
            self,
            option_type:            int,
            spot:                   Union[int, float],
            strike:                 Union[int, float],
            payoff:                 Union[int, float],
            r:                      Union[int, float],
            q:                      Union[int, float],
            vol:                    Union[int, float],
            val_date:               Union[int, float],
            end_date:               Union[int, float],
            year_base:              Union[int, float] = 245,
    ):
        """

        :param option_type: 期权类型(OptionType.CALL/OptionType.PUT)
        :param spot:        标的现价
        :param strike:      执行价格
        :param payoff:      赔付
        :param r:           无风险利率
        :param q:           股息率
        :param vol:         波动率
        :param val_date:    估值日
        :param end_date:    到期日
        :param year_base:   年化天数
        """

        super().__init__()
        self.option_type = option_type
        self.spot = spot
        self.strike = strike
        self.payoff = payoff
        self.r = r
        self.q = q
        self.vol = vol
        self.val_date = val_date
        self.end_date = end_date
        self.year_base = year_base
        self.sign = 1 if self.option_type == OptionType.CALL else -1
        self.dt = 1 / self.year_base

    def get_pv(self) -> Union[int, float]:
        if self.val_date < self.end_date:
            term = (self.end_date - self.val_date) / self.year_base
            d1 = (log(self.spot / self.strike) + (self.r - self.q + pow(self.vol, 2) / 2.0) * term) / (
                    self.vol * sqrt(term))
            d2 = d1 - self.vol * sqrt(term)
            pv = self.payoff * exp(-1 * self.r * term) * norm.cdf(self.sign * d2)
        else:
            pv = self.payoff if self.sign * (self.spot - self.strike) >= 0 else 0
        return pv




