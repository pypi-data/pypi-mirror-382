import pytest
import polars as pl
from pathlib import Path
from pommes_craft.core.model import EnergyModel
from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand
from pommes_craft.components.storage_technology import StorageTechnology
from pommes_craft.components.time_step_manager import TimeStepManager
from pommes_craft.components.economic_hypothesis import EconomicHypothesis
from pommes_craft.components.load_shedding import LoadShedding


def test_energy_model_get_results():
    """Test that results can be retrieved from the model."""
    # Create and run a simple model
    model = EnergyModel(
        name="test_results_model",
        hours=list(range(12)),  # A simple 12-hour period for faster tests
        year_ops=[2020],  # Single operational year
        year_invs=[2020],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        modes=[],  # No operation modes for simplicity
        resources=["electricity"],  # A basic resource
    )

    with model.context():
        # Add economic hypothesis for discount rate
        EconomicHypothesis("eco", discount_rate=0.05, year_ref=2020, planning_step=20)

        # Add time step manager
        TimeStepManager("ts_m", time_step_duration=1.0, operation_year_duration=12.0)

        area = Area("test_area")

        # Create a simple electricity demand
        electricity_demand_data = [
            {"hour": h, "year_op": 2020, "demand": 100}
            for h in model.hours
        ]
        electricity_demand = Demand(
            name="electricity_demand",
            resource="electricity",
            demand=pl.DataFrame(electricity_demand_data),
        )

        # Add demand to area
        area.add_component(electricity_demand)

        load_shedding = LoadShedding(name="electricity_load_shedding",
                                     resource="electricity",
                                     max_capacity=120., cost=10.)
        # Add load shedding to area
        area.add_component(load_shedding)

    # Run the model
    model.run()
