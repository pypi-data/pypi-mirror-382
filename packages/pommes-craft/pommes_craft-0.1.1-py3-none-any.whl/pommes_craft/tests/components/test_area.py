import polars as pl
import numpy as np
import pytest
from numpy.random import default_rng

from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand

from pommes_craft.components.conversion_technology import ConversionTechnology
from pommes_craft.components.storage_technology import StorageTechnology


def test_area_add_demand(energy_model):
    # Create an Area instance
    rng = default_rng(seed=0)
    # Create a simple demand DataFrame with required columns
    demand_data = pl.DataFrame(
        {
            "hour": list(range(24)) * 3,
            "year_op": [2020] * 24 + [2030] * 24 + [2040] * 24,
            "demand": 20. * rng.random(24 * 3),
        }
    )

    with energy_model.context():
        area = Area(name="test_area")
        # Create a Demand object
        electricity_demand = Demand(
            name="residential_electricity", resource="electricity", demand=demand_data
        )

    # Test adding a demand
    area.add_component(electricity_demand)

    # Verify demand was added correctly
    assert "residential_electricity" in area.components
    assert np.allclose(area.components["residential_electricity"].demand['demand'], electricity_demand.demand['demand'])

    with energy_model.context():
    # Test adding a duplicate demand raises ValueError
        duplicate_demand = Demand(
            name="residential_electricity",
            resource="electricity",  # Same resource as before
            demand=demand_data,
        )

    with pytest.raises(ValueError) as exc_info:
        area.add_component(duplicate_demand)

    # Check error message contains expected information
    assert "electricity" in str(exc_info.value)
    assert "test_area" in str(exc_info.value)

    with energy_model.context():
        # Test adding a different resource works
        heat_demand = Demand(
            name="heat_demand",
            resource="heat",
            demand=demand_data,
        )

    area.add_component(heat_demand)

    # Verify second demand was added correctly
    assert "heat_demand" in area.components
    assert len(area.components) == 2


def test_area_add_conversion_technology(energy_model):

    with energy_model.context():
        # Create an Area instance
        area = Area(name="test_area")

        # Create a ConversionTechnology object
        gas_turbine = ConversionTechnology(
            name="gas_turbine",
            factor={
                "electricity": 1.0,
                "methane": -1.82,
            },
        )

    # Test adding a conversion technology
    area.add_component(gas_turbine)

    # Verify technology was added correctly
    assert "gas_turbine" in area.components
    assert area.components["gas_turbine"] == gas_turbine

    with energy_model.context():
        # Test adding a duplicate technology raises ValueError
        duplicate_tech = ConversionTechnology(
            name="gas_turbine",
            factor={
                "electricity": 1.0,
                "methane": -1.82,
            },
        )  # Same name as before

    with pytest.raises(ValueError) as exc_info:
        area.add_component(duplicate_tech)

    # Check error message contains expected information
    assert "gas_turbine" in str(exc_info.value)
    assert "test_area" in str(exc_info.value)

    with energy_model.context():
        # Test adding a different technology works
        solar_pv = ConversionTechnology(
            name="solar_pv",
            factor={
                "electricity": 1.0,
            },
        )
    area.add_component(solar_pv)

    # Verify second technology was added correctly
    assert "solar_pv" in area.components
    assert len(area.components) == 2


def test_area_add_storage_technology(energy_model):


    with energy_model.context():
        # Create an Area instance
        area = Area(name="test_area")

        # Create a StorageTechnology object
        battery = StorageTechnology(
            name="battery",
            factor_in={"electricity": 1.0},  # Example value, adjust based on your needs
            factor_keep={"electricity": 0.9},  # Example value, adjust based on your needs
            factor_out={"electricity": 0.8},  # Example value, adjust based on your needs
        )

    # Test adding a storage technology
    area.add_component(battery)

    # Verify technology was added correctly
    assert "battery" in area.components
    assert area.components["battery"] == battery

    with energy_model.context():
        # Test adding a duplicate technology raises ValueError
        duplicate_tech = StorageTechnology(
            name="battery",
            factor_in={"electricity": 1.0},  # Example value, adjust based on your needs
            factor_keep={"electricity": 0.9},  # Example value, adjust based on your needs
            factor_out={"electricity": 0.8},
        )  # Same name as before

    with pytest.raises(ValueError) as exc_info:
        area.add_component(duplicate_tech)

    # Check error message contains expected information
    assert "battery" in str(exc_info.value)
    assert "test_area" in str(exc_info.value)

    with energy_model.context():
        # Test adding a different technology works
        pumped_hydro = StorageTechnology(
            name="pumped_hydro",
            factor_in={"electricity": 1.0},  # Example value, adjust based on your needs
            factor_keep={"electricity": 0.9},  # Example value, adjust based on your needs
            factor_out={"electricity": 0.8},
        )
        area.add_component(pumped_hydro)

    # Verify second technology was added correctly
    assert "pumped_hydro" in area.components
    assert len(area.components) == 2
