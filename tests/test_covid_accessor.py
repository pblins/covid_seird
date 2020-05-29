"""Test module."""
from os.path import isfile
from unittest import TestCase

import pandas as pd
from requests.exceptions import HTTPError

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
        """Test country_search with single return."""
        expected = {"BR": "Brazil"}
        result = CountryCovidSeird.country_search("brazil")
        self.assertEqual(expected, result)

    def test_search_multiple_returns(self):
        """Test country_search with multiple returns."""
        expected = {"AE": "United Arab Emirates", "GB": "United Kingdom"}
        result = CountryCovidSeird.country_search("united")
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
        self.assertIsNone(self.result.r2)
        self.assertIsNone(self.result.r0)
        self.assertIsNone(self.result.best_fit)

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
            "/home/prlins/Documentos/covid_seird_model/test_plot_fit"
        )
        self.assertTrue(
            isfile(
                "/home/prlins/Documentos/covid_seird_model/test_plot_fit.png"
            )
        )

    def test_simulation(self):
        """Test simulation method."""
        self.result.fit()
        self.result.simulation(days_ahead=150)
        self.assertIsNotNone(self.result._CountryCovidSeird__simulation_return)

    def test_plot_simulation(self):
        """Test plot simulation method."""
        self.result.fit()
        self.result.simulation(days_ahead=150)
        self.result.plot_simulation(
            "/home/prlins/Documentos/covid_seird_model/test_plot_simulation"
        )
        self.assertTrue(
            isfile(
                "/home/prlins/Documentos/covid_seird_model/test_plot_simulation.png"
            )
        )
