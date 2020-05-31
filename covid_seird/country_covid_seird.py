"""Covid accessor."""
import COVID19Py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.integrate import odeint
from lmfit import Model, Parameters


class CountryCovidSeird:
    """Country class."""

    __covid_data = COVID19Py.COVID19(data_source="jhu")
    __location_dict = dict(
        zip(
            list(
                map(lambda x: x["country_code"], __covid_data.getLocations())
            ),
            list(map(lambda x: x["country"], __covid_data.getLocations())),
        )
    )

    def __init__(self, code: str):
        """Class initialization."""
        country_data = CountryCovidSeird.__covid_data.getLocationByCountryCode(
            code.upper(), timelines=True
        )
        index = list(
            country_data[0]["timelines"]["confirmed"]["timeline"].keys()
        )
        confirmed = country_data[0]["timelines"]["confirmed"][
            "timeline"
        ].values()
        deaths = country_data[0]["timelines"]["deaths"]["timeline"].values()

        self.__fit_return = None
        self.__simulation_return = None
        self.__name = country_data[0]["country"]
        self.__code = country_data[0]["country_code"]
        self.__population = country_data[0]["country_population"]
        self.__data = pd.DataFrame(
            data={"confirmed": list(confirmed), "deaths": list(deaths)},
            index=index,
        )
        self.__data = self.__data[self.__data["confirmed"] > 0]

    @classmethod
    def code_search(cls, country_string: str) -> dict:
        """Search country code by country name."""
        return dict(
            (k, v)
            for k, v in cls.__location_dict.items()
            if country_string.lower() in v.lower()
        )

    @property
    def name(self):
        """Get the name."""
        return self.__name

    @property
    def code(self):
        """Get the code."""
        return self.__code

    @property
    def population(self):
        """Get the population size."""
        return self.__population

    @property
    def data(self):
        """Get the covid data."""
        return self.__data

    @property
    def best_fit(self):
        """Get best fit."""
        return (
            np.array(
                [i * self.population for i in self.__fit_return["best_fit"]]
            )
            if self.__fit_return is not None
            else None
        )

    @property
    def r0(self):
        """Get r0."""
        return (
            self.__fit_return["r0"] if self.__fit_return is not None else None
        )

    @property
    def r2(self):
        """Get r2."""
        return (
            self.__fit_return["r2"] if self.__fit_return is not None else None
        )

    @property
    def curves(self):
        """Get SEIRD simulation curves."""
        return (
            pd.DataFrame(
                data={
                    "susceptible": self.__simulation_return["S"],
                    "exposed": self.__simulation_return["E"],
                    "infected": self.__simulation_return["I"],
                    "recovered": self.__simulation_return["R"],
                    "dead": self.__simulation_return["D"],
                }
            )
            if self.__simulation_return is not None
            else None
        )

    def fit(self):
        """Fit the real data into the SEIRD model."""
        if self.__fit_return is None:
            scaled_cases = np.array(
                [i / self.population for i in self.data["confirmed"]]
            )
            x = np.linspace(0.0, len(scaled_cases), len(scaled_cases))

            params = Parameters()
            params.add("r0", value=2.0, min=0.0)
            params.add("gamma", value=0.1, min=0.0, max=1.0)
            params.add("delta", value=0.1, min=0.0, max=1.0)
            params.add("alpha", value=0.1, min=0.0, max=1.0)
            params.add("rho", value=0.1, min=0.0, max=1.0)
            params.add("population", value=self.population, vary=False)
            params.add("fit", value=True, vary=False)

            mod = Model(_seird)
            model_return = mod.fit(scaled_cases, params, x=x)
            _, _, r_value, _, _ = linregress(
                model_return.best_fit, scaled_cases
            )
            self.__fit_return = {
                "best_fit": model_return.best_fit,
                "r0": model_return.best_values["r0"],
                "r2": r_value ** 2,
                "gamma": model_return.best_values["gamma"],
                "delta": model_return.best_values["delta"],
                "alpha": model_return.best_values["alpha"],
                "rho": model_return.best_values["rho"],
            }

    def plot_fit(self, filename: str = ""):
        """Plot fit curve."""
        if self.__fit_return is not None:

            x = pd.to_datetime(self.data.index)

            plt.figure(figsize=(10, 4))
            plt.plot_date(x, self.data["confirmed"], "-")
            plt.plot(x, self.best_fit)
            plt.legend(
                [
                    "real",
                    "fit (R2: {:.2f} | R0: {:.2f})".format(self.r2, self.r0),
                ]
            )
            plt.title("{} - SEIRD model fit".format(self.name))
            plt.xlabel("time (since first confirmed infection)")
            plt.ylabel("population")
            if len(filename) != 0:
                plt.savefig("{}.png".format(filename))
            return plt

    def simulation(self, days_ahead: int = 100):
        """Compute the seird model simulation curves."""
        if self.__fit_return is not None:
            scaled_cases = np.array(
                [i / self.population for i in self.data["confirmed"]]
            )
            x = np.linspace(
                0.0,
                len(scaled_cases) + days_ahead,
                len(scaled_cases) + days_ahead,
            )
            S, E, I, R, D = _seird(
                x,
                self.r0,
                self.__fit_return["gamma"],
                self.__fit_return["delta"],
                self.__fit_return["alpha"],
                self.__fit_return["rho"],
                population=self.population,
                fit=False,
            )

            self.__simulation_return = {"S": S, "E": E, "I": I, "R": R, "D": D}

    def plot_simulation(self, filename: str = ""):
        """Plot SEIRD simulation curves."""
        if self.__simulation_return is not None:

            real_data = pd.to_datetime(self.data.index)
            x = pd.date_range(
                start=real_data[0], periods=len(self.curves["susceptible"]),
            )

            f, ax = plt.subplots(1, 1, figsize=(10, 4))
            ax.plot_date(
                x,
                list(
                    map(
                        lambda x: x * self.population,
                        self.curves["susceptible"],
                    )
                ),
                "b",
                alpha=0.7,
                linewidth=2,
                label="susceptible",
            )
            ax.plot_date(
                x,
                list(
                    map(lambda x: x * self.population, self.curves["exposed"],)
                ),
                "y",
                alpha=0.7,
                linewidth=2,
                label="exposed",
            )
            ax.plot_date(
                x,
                list(
                    map(
                        lambda x: x * self.population, self.curves["infected"],
                    )
                ),
                "r",
                alpha=0.7,
                linewidth=2,
                label="infected",
            )
            ax.plot_date(
                x,
                list(
                    map(
                        lambda x: x * self.population,
                        self.curves["recovered"],
                    )
                ),
                "g",
                alpha=0.7,
                linewidth=2,
                label="recovered",
            )
            ax.plot_date(
                x,
                list(map(lambda x: x * self.population, self.curves["dead"],)),
                "k",
                alpha=0.7,
                linewidth=2,
                label="dead",
            )

            ax.set_ylabel("population")
            ax.set_xlabel("time (since first confirmed infection)")

            ax.yaxis.set_tick_params(length=0)
            ax.xaxis.set_tick_params(length=0)
            ax.grid(b=True, which="major", c="w", lw=2, ls="-")
            legend = ax.legend()
            legend.get_frame().set_alpha(0.5)
            for spine in ("top", "right", "bottom", "left"):
                ax.spines[spine].set_visible(False)

            plt.title("{} - SEIRD Simulation".format(self.name))
            if len(filename) != 0:
                plt.savefig("{}.png".format(filename))
            return plt


def _seird(x, r0, gamma, delta, alpha, rho, population, fit):
    def deriv(y, x, r0, gamma, delta, alpha, rho):
        beta = r0 * gamma
        S, E, I, R, D = y
        dSdt = -beta * S * I
        dEdt = beta * S * I - delta * E
        dIdt = delta * E - (1 - alpha) * gamma * I - alpha * rho * I
        dRdt = (1 - alpha) * gamma * I
        dDdt = alpha * rho * I
        return dSdt, dEdt, dIdt, dRdt, dDdt

    I0 = 1 / population
    S0 = 1 - I0
    y0 = [S0, I0, I0, 0.0, 0.0]
    ysol = odeint(deriv, y0, x, args=(r0, gamma, delta, alpha, rho))

    S, E, I, R, D = ysol.T
    if fit:
        return I
    else:
        return [S, E, I, R, D]
