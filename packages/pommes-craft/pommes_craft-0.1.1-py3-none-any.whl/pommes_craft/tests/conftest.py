import pytest
from pommes_craft.core.model import EnergyModel


@pytest.fixture
def energy_model():
    """
    Create and return a basic EnergyModel instance for testing storage technologies.
    """
    model = EnergyModel(
        name="test_model",
        hours=list(range(24)),  # A simple 24-hour period
        year_ops=[2020, 2030, 2040],  # Single operational year
        year_invs=[2020, 2030, 2040],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        modes=["normal"],  # Single operation mode
        resources=["electricity", "methane"],  # A basic resource
    )
    return model
