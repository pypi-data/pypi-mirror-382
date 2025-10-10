import polars as pl
import numpy as np

from pommes_craft import test_data_path
from pommes_craft.core.model import EnergyModel
from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand
from pommes_craft.components.economic_hypothesis import EconomicHypothesis
from pommes_craft.components.conversion_technology import ConversionTechnology
from pommes_craft.components.time_step_manager import TimeStepManager
from pommes_craft.components.spillage import Spillage
from pommes_craft.components.load_shedding import LoadShedding


def test_one_area_conversion_tech():
    """
    Test a simple energy system with two zones, electricity demands for each zone,
    and a gas turbine in one of the zones.
    """
    rng = np.random.default_rng(seed=0)
    # Create energy model
    energy_model = EnergyModel(
        name="one_area_conversion_tech",
        folder=test_data_path / "one_area_conversion_tech",
        hours=list(range(24)),  # 24-hour period
        year_ops=[2020, 2040],  # Two operation years
        year_invs=[2020],  # Single investment year
        year_decs=[2050],  # Single decommissioning year
        modes=[],  # No operation mode
        resources=["electricity", "methane"],  # Basic resources
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
        # Add demands to area
        area1.add_component(electricity_demand1)

        load_shedding = LoadShedding(
            name="electricity_load_shedding",
            resource="electricity",
            max_capacity=0.,
            cost=0.
        )
        area1.add_component(load_shedding)

        # Create gas turbine in area1
        gas_turbine = ConversionTechnology(
            name="gas_turbine",
            factor={
                    "electricity": 1.0,  # Produces electricity
                    "methane": -2.0  # Consumes methane (negative factor)
            },
            life_span=30.,
            variable_cost=70.,
            invest_cost=800.,
        )

        # Add conversion technology to area1
        area1.add_component(gas_turbine)

    # Verify the model structure and components
    # Check areas have the correct components
    assert "electricity_demand_area1" in area1.components

    energy_model.run()
    pass
