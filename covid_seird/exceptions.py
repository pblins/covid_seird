"""Exceptions related to covid-seird package."""


class NoFitError(Exception):
    """fit() method needs to be called."""

    def __init__(self):
        """Exception initialization."""
        super().__init__("No fit was found.")


class NoSimulationError(Exception):
    """simulation() method needs to be called."""

    def __init__(self):
        """Exception initialization."""
        super().__init__("No simulation was found.")
