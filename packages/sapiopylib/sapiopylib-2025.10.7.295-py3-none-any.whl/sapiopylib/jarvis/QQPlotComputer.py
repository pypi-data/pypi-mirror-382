import json
from typing import List, Any, Dict

import numpy as np
from numpyencoder import NumpyEncoder
from scipy import stats


class QQPlotComputer:
    """
    Computes Quantile-Quantile data for a given population.
    In this plot, x is the theoretical quantile (of target distribution) and y is the observed quantiles (from data).
    """
    _original_data: List[float]
    _confidence: float
    _dist: Any
    _upper: List[float]
    _lower: List[float]
    _r_squared: float
    _theo_quantile_x: List[float]
    _observed_quantile_y: List[float]
    _slope_regression: float
    _intercept_regression: float

    @property
    def original_data(self):
        """
        Get the original data that were input of the QQ plot computer.
        """
        return self._original_data

    @property
    def upper_observed_list(self):
        """
        Get the upper limit of acceptable value in the Q-Q plot so that the original data is thought to be
         fitted to the target distribution.
        """
        return self._upper

    @property
    def lower_observed_list(self):
        """
        Get the lower limit of acceptable value in the Q-Q plot so that the original data is thought to be
         fitted to the target distribution.
        """
        return self._lower

    @property
    def r_squared(self):
        """
        Get the R-Squared of the regression of Q-Q fit.
        """
        return self._r_squared

    @property
    def slope_of_regression(self):
        """
        Get the slope of the regression of Q-Q fit.
        """
        return self._slope_regression

    @property
    def intercept_of_regression(self):
        """
        Get the intercept of the regression of Q-Q fit.
        """
        return self._intercept_regression

    @property
    def scatter_x_list(self):
        """
        Get the scatter plot in the Q-Q, X-axis. (theoretical quantile raw points)
        """
        return self._theo_quantile_x

    @property
    def scatter_y_list(self):
        """
        Get the scatter plots in the Q-Q, Y-axis. (observed quantile raw points)
        """
        return self._observed_quantile_y

    def __init__(self, original_data: List[float], confidence: float = 0.95, dist: str = "norm"):
        self._original_data = original_data
        self._confidence = confidence
        self._dist = getattr(stats, dist)
        self._compute_qq()

    @staticmethod
    def _ppoints(n, a=0.5):
        a = 3 / 8 if n <= 10 else 0.5
        return (np.arange(n) + 1 - a) / (n + 1 - 2 * a)

    def _compute_qq(self):
        quantiles = stats.probplot(self._original_data, sparams=(), dist=self._dist, fit=False)
        theor, observed = quantiles[0], quantiles[1]
        # Theoretical = x, Observed = y
        slope, intercept, r, _, _ = stats.linregress(theor, observed)
        self._theo_quantile_x = theor
        self._observed_quantile_y = observed
        self._slope_regression = slope
        self._intercept_regression = intercept
        self._r_squared = r ** 2
        fit_params = self._dist.fit(self._original_data)
        loc = fit_params[-2]
        scale = fit_params[-1]
        shape = fit_params[:-2] if len(fit_params) > 2 else None
        fit_val = slope * theor + intercept
        n = len(self._original_data)
        P = self._ppoints(n)
        crit = stats.norm.ppf(1 - (1 - self._confidence) / 2)
        pdf = self._dist.pdf(theor) if shape is None else self._dist.pdf(theor, *shape)
        se = (slope / pdf) * np.sqrt(P * (1 - P) / n)
        self._upper = fit_val + crit * se
        self._lower = fit_val - crit * se

    def get_regression_by_x(self, x: float):
        return self.slope_of_regression * x + self.intercept_of_regression

    def to_json(self) -> Dict[str, Any]:
        return {
            'originalData': self.original_data,
            'r_squared': self._r_squared,
            'upper': self._upper,
            'lower': self._lower,
            'slopeOfRegression': self.slope_of_regression,
            'interceptOfRegression': self.intercept_of_regression,
            'theoreticalQuantileX': self._theo_quantile_x,
            'observedQuantileY': self._observed_quantile_y
        }

    def __str__(self):
        return json.dumps(self.to_json(), cls=NumpyEncoder)