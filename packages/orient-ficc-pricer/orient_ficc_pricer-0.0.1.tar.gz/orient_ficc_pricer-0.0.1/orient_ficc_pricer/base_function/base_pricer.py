import numpy as np
from typing import Union, Tuple, Dict
from scipy.stats import norm
from math import sqrt, log, exp
from orient_ficc_pricer.base_function.protos import *


class BasePricer:

    """
        适用于解析解计算pv的期权 -- 差分法计算希腊字母
    """

    spot:           Union[int, float]
    r:              Union[int, float]
    q:              Union[int, float]
    vol:            Union[int, float]
    val_date:       Union[int, float]
    end_date:       Union[int, float]

    def __init__(self):

        self.ds = 0.01
        self.dv = 0.01
        self.dr = 0.0001
        self.dq = 0.001

    def get_pv(self) -> Union[int, float]:
        return 0.

    def get_delta(self) -> Union[int, float]:
        ds = self.ds
        spot0 = self.spot
        spot1 = self.spot * (1 - ds)
        spot2 = self.spot * (1 + ds)
        self.spot = spot1
        pv1 = self.get_pv()
        self.spot = spot2
        pv2 = self.get_pv()
        self.spot = spot0
        delta = (pv2 - pv1) / (2 * spot0 * ds)
        return delta

    def get_gamma(self) -> Union[int, float]:
        ds = self.ds
        spot0 = self.spot
        spot1 = self.spot * (1 - ds)
        spot2 = self.spot * (1 + ds)
        pv0 = self.get_pv()
        self.spot = spot1
        pv1 = self.get_pv()
        self.spot = spot2
        pv2 = self.get_pv()
        self.spot = spot0
        gamma = (pv2 - 2 * pv0 + pv1) / (spot0 * ds) ** 2
        return gamma

    def get_delta_gamma(self) -> Tuple:
        ds = self.ds
        spot0 = self.spot
        spot1 = self.spot * (1 - ds)
        spot2 = self.spot * (1 + ds)
        pv0 = self.get_pv()
        self.spot = spot1
        pv1 = self.get_pv()
        self.spot = spot2
        pv2 = self.get_pv()
        self.spot = spot0
        delta = (pv2 - pv1) / (2 * spot0 * ds)
        gamma = (pv2 - 2 * pv0 + pv1) / (spot0 * ds) ** 2
        return delta, gamma

    def get_vega(self) -> Union[int, float]:
        dvol = self.dv
        vol0 = self.vol
        vol2 = vol0 + dvol
        pv0 = self.get_pv()
        self.vol = vol2
        vol2 = self.get_pv()
        self.vol = vol0
        vol = vol2 - pv0
        return vol

    def get_theta(self) -> Union[int, float]:
        if self.val_date < self.end_date:
            dt = 1
        else:
            dt = 0
        t0 = self.val_date
        t2 = t0 + dt
        pv0 = self.get_pv()
        self.val_date = t2
        pv2 = self.get_pv()
        theta = pv2 - pv0
        return theta

    def get_rho(self) -> Union[int, float]:
        r0 = self.r
        r2 = self.r + self.dr
        pv0 = self.get_pv()
        self.r = r2
        pv2 = self.get_pv()
        rho = pv2 - pv0
        self.r = r0
        return rho

    def get_phi(self) -> Union[int, float]:
        q0 = self.q
        q2 = self.q + self.dq
        pv0 = self.get_pv()
        self.q = q2
        pv2 = self.get_pv()
        phi = pv2 - pv0
        self.q = q0
        return phi

    def get_dddt(self) -> Union[int, float]:
        spot0 = self.spot
        spot1 = spot0 * (1 - self.ds)
        spot2 = spot0 * (1 + self.ds)

        delta_t1 = self.get_delta()
        if self.val_date < self.end_date:
            dt = 1
            t0 = self.val_date
            t2 = t0 + dt
            self.val_date = t2
            self.spot = spot1
            pv_spot1_t2 = self.get_pv()
            self.spot = spot2
            pv_spot2_t2 = self.get_pv()
            self.spot = spot0
            self.val_date = t0
            delta_t2 = (pv_spot2_t2 - pv_spot1_t2) / (2 * spot0 * self.ds)
        else:
            delta_t2 = 0

        dddt = delta_t2 - delta_t1

        return dddt

    def get_dddq(self) -> Union[int, float]:
        spot0 = self.spot
        spot1 = spot0 * (1 - self.ds)
        spot2 = spot0 * (1 + self.ds)

        delta_q1 = self.get_delta()
        q0 = self.q
        self.q = q0 + self.dq
        self.spot = spot1
        pv_spot1_q2 = self.get_pv()
        self.spot = spot2
        pv_spot2_q2 = self.get_pv()
        self.spot = spot0
        self.q = q0
        delta_q2 = (pv_spot2_q2 - pv_spot1_q2) / (2 * spot0 * self.ds)

        dddq = delta_q2 - delta_q1
        return dddq

    def get_greeks(self) -> Dict:
        greeks = {'delta': 0, 'gamma': 0, 'vega': 0, 'theta': 0, 'rho': 0, 'phi': 0, 'dddt': 0, 'dddq': 0}

        pv0 = self.get_pv()
        ds = self.ds
        spot0 = self.spot
        spot1 = self.spot * (1 - ds)
        spot2 = self.spot * (1 + ds)
        self.spot = spot1
        pv_spot1 = self.get_pv()
        self.spot = spot2
        pv_spot2 = self.get_pv()
        self.spot = spot0
        greeks['delta'] = (pv_spot2 - pv_spot1) / (2 * spot0 * ds)
        greeks['gamma'] = (pv_spot2 - 2 * pv0 + pv_spot1) / (spot0 * ds) ** 2

        vol0 = self.vol
        vol2 = vol0 + self.dv
        self.vol = vol2
        pv_vol2 = self.get_pv()
        self.vol = vol0
        greeks['vega'] = pv_vol2 - pv0

        if self.val_date < self.end_date:
            dt = 1
            t0 = self.val_date
            t2 = t0 + dt
            self.val_date = t2
            pv_t2 = self.get_pv()
            self.spot = spot1
            pv_spot1_t2 = self.get_pv()
            self.spot = spot2
            pv_spot2_t2 = self.get_pv()
            self.spot = spot0
            self.val_date = t0
            delta_t2 = (pv_spot2_t2 - pv_spot1_t2) / (2 * spot0 * ds)
            greeks['theta'] = pv_t2 - pv0

        else:
            greeks['theta'] = 0
            delta_t2 = 0

        greeks['dddt'] = delta_t2 - greeks['delta']

        r0 = self.r
        r2 = self.r + self.dr
        self.r = r2
        pv_r2 = self.get_pv()
        self.r = r0
        greeks['rho'] = pv_r2 - pv0

        q0 = self.q
        q2 = self.q + self.dq
        self.q = q2
        pv_q2 = self.get_pv()
        self.spot = spot1
        pv_spot1_q2 = self.get_pv()
        self.spot = spot2
        pv_spot2_q2 = self.get_pv()
        self.spot = spot0
        self.q = q0
        delta_q2 = (pv_spot2_q2 - pv_spot1_q2) / (2 * spot0 * self.ds)
        greeks['phi'] = pv_q2 - pv0
        greeks['dddq'] = delta_q2 - greeks['delta']

        return greeks


