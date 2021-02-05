"""Test module."""
from os.path import isfile
from unittest import TestCase

import pandas as pd
from requests.exceptions import HTTPError

from covid_seird.exceptions import (NoFitError,
                                    NoSimulationError)
from covid_seird.country_covid_seird import CountryCovidSeird


class CountryCovidSeirdTestBase(TestCase):
    """Base covid test class."""

    def setUp(self):
        """Set up."""
        self.result = CountryCovidSeird("br")

    def tearDown(self):
        """Tear down."""
        del self.result


class CountryCovidSeirdTest(CountryCovidSeirdTestBase):
    """Test the covid accessor."""

    def test_search_single_return(self):
        """Test code_search with single return."""
        expected = {"BR": "Brazil"}
        result = CountryCovidSeird.code_search("brazil")
        self.assertEqual(expected, result)

    def test_search_multiple_returns(self):
        """Test code_search with multiple returns."""
        expected = {"AE": "United Arab Emirates", "GB": "United Kingdom"}
        result = CountryCovidSeird.code_search("united")
        self.assertEqual(expected, result)

    def test_country_covid_seird_initialization_not_ok(self):
        """Test CountryCovidSeird invalid initialization method."""
        with self.assertRaises(HTTPError):
            CountryCovidSeird("mvmvm")

    def test_country_covid_seird_initialization_ok(self):
        """Test CountryCovidSeird valid initialization method."""
        self.assertTrue(isinstance(self.result, CountryCovidSeird))

    def test_country_covid_seird_getters(self):
        """Test CountryCovidSeird getters."""
        name = "Brazil"
        code = "BR"
        population = 209469333

        self.assertEqual(name, self.result.name)
        self.assertEqual(code, self.result.code)
        self.assertEqual(population, self.result.population)
        self.assertTrue(isinstance(self.result.data, pd.DataFrame))
        self.assertFalse(self.result.data.empty)

    def test_fit_no_call(self):
        """Test no fit exception."""
        with self.assertRaises(NoFitError):
            self.result.r0
        with self.assertRaises(NoFitError):
            self.result.r2
        with self.assertRaises(NoFitError):
            self.result.best_fit

    def test_fit(self):
        """Test fit method."""
        self.result.fit()
        self.assertIsNotNone(self.result.r2)
        self.assertIsNotNone(self.result.r0)
        self.assertIsNotNone(len(self.result.best_fit))

    def test_plot_fit(self):
        """Test plot fit method."""
        self.result.fit()
        self.result.plot_fit(
            "./test_plot_fit"
        )
        self.assertTrue(
            isfile(
                "./test_plot_fit.png"
            )
        )

    def test_fit_no_simulation(self):
        """Test no fit exception."""
        with self.assertRaises(NoSimulationError):
            self.result.curves

    def test_simulation(self):
        """Test simulation method."""
        self.result.fit()
        self.result.simulation(days_ahead=150)
        self.assertIsNotNone(self.result.curves)

    def test_plot_simulation(self):
        """Test plot simulation method."""
        self.result.fit()
        self.result.simulation(days_ahead=150)
        self.result.plot_simulation(
            "./test_plot_simulation"
        )
        self.assertTrue(
            isfile(
                "./test_plot_simulation.png"
            )
        )
