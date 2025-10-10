import polars as pl
import numpy as np

from pommes_craft import test_data_path
from pommes_craft.core.model import EnergyModel
from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand
from pommes_craft.components.economic_hypothesis import EconomicHypothesis
from pommes_craft.components.storage_technology import StorageTechnology
from pommes_craft.components.conversion_technology import ConversionTechnology
from pommes_craft.components.time_step_manager import TimeStepManager


def test_one_area_storage_tech():
    """
    Test a simple energy system with one area, electricity demand,
    and a battery storage technology.
    """
    rng = np.random.default_rng(seed=0)
    # Create energy model
    energy_model = EnergyModel(
        name="one_area_storage_tech",
        folder=test_data_path / "one_area_storage_tech",
        hours=list(range(24)),  # 24-hour period
        year_ops=[2020, 2040],  # Two operation years
        year_invs=[2020],  # Single investment year
        year_decs=[2050],  # Single decommissioning year
        modes=[],  # No operation mode
        resources=["electricity"],  # Basic resource
    )

    with energy_model.context():
        EconomicHypothesis("eco", discount_rate=0., year_ref=2020, planning_step=20)
        TimeStepManager("ts_m", time_step_duration=1., operation_year_duration=24.)
        area1 = Area("area1")

        # Create electricity demand profiles
        electricity_demand_data1 = [
            {"hour": h, "year_op": y, "demand": 100 * rng.random()}
            for h in energy_model.hours
            for y in energy_model.year_ops
        ]
        electricity_demand1 = Demand(
            name="electricity_demand_area1",
            resource="electricity",
            demand=pl.DataFrame(electricity_demand_data1),
        )

        # Add demand to area
        area1.add_component(electricity_demand1)

        # Create battery storage technology
        battery_storage = StorageTechnology(
            name="battery_storage",
            factor_in={"electricity": -1.0},  # Consumes electricity when charging
            factor_out={"electricity": 0.9},  # Produces electricity when discharging (with 90% efficiency)
            factor_keep={"electricity": 0.99},  # Self-discharge rate (99% retention per hour)
            life_span=30.,  # 30-year lifespan
            invest_cost_energy=200.,  # Cost per MWh of storage capacity
            invest_cost_power=100.,  # Cost per MW of power capacity
        )

        # Add storage technology to area
        area1.add_component(battery_storage)

        # Add electricity prod with capacity lower than max demand
        elec_production = ConversionTechnology(
            name='elec_production',
            factor={'electricity': 1.0},
            power_capacity_investment_max=50,
            life_span=30.,
        )
        area1.add_component(elec_production)

    # Verify the model structure and components
    assert "electricity_demand_area1" in area1.components
    assert "battery_storage" in area1.components

    energy_model.run()
    pass
