import pytest
import polars as pl
import numpy as np

from pommes_craft import ConversionTechnology
from pommes_craft import test_data_path
from pommes_craft.core.model import EnergyModel
from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand
from pommes_craft.components.economic_hypothesis import EconomicHypothesis
from pommes_craft.components.combined_techology import CombinedTechnology
from pommes_craft.components.time_step_manager import TimeStepManager
from pommes_craft.components.net_import import NetImport


def test_one_area_combined_tech():
    """
    Test a simple energy system with two zones, electricity demands for each zone,
    and a gas turbine in one of the zones.
    """
    rng = np.random.default_rng(seed=0)
    # Create energy model
    energy_model = EnergyModel(
        name="one_area_combined_tech",
        folder=test_data_path / "one_area_combined_tech",
        hours=list(range(24)),  # 24-hour period
        year_ops=[2020, 2040],  # Two operation years
        year_invs=[2020, 2040],  # Two investment year
        year_decs=[2070],  # Single decommissioning year
        modes=["electric", "fossil"],  # Two operation modes
        resources=["electricity", "methane", "heat"],  # Basic resources
    )

    with energy_model.context():
        EconomicHypothesis("eco", discount_rate=0., year_ref=2020, planning_step=20)
        TimeStepManager("ts_m", time_step_duration=1., operation_year_duration=24.)
        area1 = Area("area1")

        # Create heat demand profiles
        heat_demand_data1 = [
            {"hour": h, "year_op": y, "demand": 100 * rng.random()}
            for h in energy_model.hours
            for y in energy_model.year_ops
        ]
        heat_demand1 = Demand(
            name="heat_demand_area1",
            resource="heat",
            demand=pl.DataFrame(heat_demand_data1),
        )
        # Add demands to area
        area1.add_component(heat_demand1)

        # elec_import = NetImport(
        #     name="elec_import",
        #     resource="electricity",
        #     import_price=80.
        # )
        # gas_import = NetImport(
        #     name="gas_import",
        #     resource="methane",
        #     import_price=30.
        # )
        # heat_import = NetImport(
        #     name="heat_import",
        #     resource="heat",
        #     max_yearly_energy_import=0.
        # )
        # Add net import to area
        # area1.add_component(elec_import)
        # area1.add_component(gas_import)
        # area1.add_component(heat_import)


        # Create gas turbine in area1
        hybrid_boiler = CombinedTechnology(
            name="hybrid_boiler",
            factor={
                "electric":{
                    "electricity": -1.0,  # Consumes electricity
                    "heat": 1.  # Produces heat (negative factor)
                },
                "fossil": {
                    "methane": -1.5,  # Consumes methane
                    "heat": 1.  # Produces heat (negative factor)
                },
            },
            emission_factor={
                "electric": 20.,
                "fossil": 200.,
            },
            variable_cost={
                "electric": 70.,
                "fossil": 15.,
            },
            invest_cost=800.,
            life_span=20.,
            power_capacity_investment_max=1000.
        )
        # Add combined technology to area1
        area1.add_component(hybrid_boiler)


    # Verify the model structure and components
    # Check areas have the correct components
    assert "heat_demand_area1" in area1.components
    assert "hybrid_boiler" in area1.components

    energy_model.run()

    print("All tests passed!")
    return energy_model, area1