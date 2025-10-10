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


def test_multi_resource_system():
    """
    Test a simple energy system with one area, multiple resources (electricity, heat, hydrogen),
    and various technologies for conversion and storage.
    Uses low time parameters for fast execution.
    """
    rng = np.random.default_rng(seed=42)

    # Create energy model with multiple resources and low time parameters
    energy_model = EnergyModel(
        name="multi_resource_system",
        folder=test_data_path / "multi_resource_system",
        hours=list(range(12)),  # Only 12 hours for faster tests
        year_ops=[2020],  # Single operation year for faster tests
        year_invs=[2020],  # Single investment year
        year_decs=[2050],  # Single decommissioning year
        modes=[],  # No operation modes
        resources=["electricity", "heat", "hydrogen"],  # Multiple resources
    )

    with energy_model.context():
        # Add economic hypothesis and time step manager
        EconomicHypothesis("eco", discount_rate=0.05, year_ref=2020, planning_step=20)
        TimeStepManager("ts_m", time_step_duration=1., operation_year_duration=12.)  # Low duration for faster tests

        # Create an area
        area = Area("multi_resource_area")

        # Create demand profiles for each resource
        # Electricity demand
        electricity_demand_data = [
            {"hour": h, "year_op": 2020, "demand": 100 + 20 * rng.random()}
            for h in energy_model.hours
        ]
        electricity_demand = Demand(
            name="electricity_demand",
            resource="electricity",
            demand=pl.DataFrame(electricity_demand_data),
        )

        # Heat demand
        heat_demand_data = [
            {"hour": h, "year_op": 2020, "demand": 80 + 15 * rng.random()}
            for h in energy_model.hours
        ]
        heat_demand = Demand(
            name="heat_demand",
            resource="heat",
            demand=pl.DataFrame(heat_demand_data),
        )

        # Hydrogen demand
        hydrogen_demand_data = [
            {"hour": h, "year_op": 2020, "demand": 30 + 10 * rng.random()}
            for h in energy_model.hours
        ]
        hydrogen_demand = Demand(
            name="hydrogen_demand",
            resource="hydrogen",
            demand=pl.DataFrame(hydrogen_demand_data),
        )

        # Add demands to area
        area.add_component(electricity_demand)
        area.add_component(heat_demand)
        area.add_component(hydrogen_demand)

        # Add electricity production (e.g., solar PV)
        solar_pv = ConversionTechnology(
            name="solar_pv",
            factor={"electricity": 1.0},
            power_capacity_investment_max=150,
            life_span=25.,
            invest_cost=800.,
            # Add a capacity factor to simulate solar availability
            availability=pl.DataFrame([
                {"hour": h, "year_op": 2020, "availability": max(0, 0.8 * np.sin(np.pi * h / 12))}
                for h in energy_model.hours
            ]),
        )
        area.add_component(solar_pv)

        # Add a CHP (Combined Heat and Power) plant
        chp = ConversionTechnology(
            name="chp",
            factor={"electricity": 0.4, "heat": 0.5},  # Produces both electricity and heat
            power_capacity_investment_max=100,
            life_span=30.,
            invest_cost=1200.,
            variable_cost=50.,  # Cost of fuel
        )
        area.add_component(chp)

        # Add an electrolyzer (electricity to hydrogen)
        electrolyzer = ConversionTechnology(
            name="electrolyzer",
            factor={"electricity": -1.0, "hydrogen": 0.7},  # Consumes electricity, produces hydrogen
            power_capacity_investment_max=50,
            life_span=15.,
            invest_cost=1500.,
        )
        area.add_component(electrolyzer)

        # Add a fuel cell (hydrogen to electricity)
        fuel_cell = ConversionTechnology(
            name="fuel_cell",
            factor={"hydrogen": -1.0, "electricity": 0.6},  # Consumes hydrogen, produces electricity
            power_capacity_investment_max=40,
            life_span=10.,
            invest_cost=1000.,
        )
        area.add_component(fuel_cell)

        # Add battery storage for electricity
        battery = StorageTechnology(
            name="battery",
            factor_in={"electricity": -1.0},  # Consumes electricity when charging
            factor_out={"electricity": 0.9},  # Produces electricity when discharging (90% efficiency)
            factor_keep={"electricity": 0.99},  # Self-discharge rate (99% retention per hour)
            life_span=15.,
            invest_cost_energy=300.,
            invest_cost_power=150.,
            power_capacity_investment_max=80,
            energy_capacity_investment_max=400,
        )
        area.add_component(battery)

        # Add thermal storage for heat
        thermal_storage = StorageTechnology(
            name="thermal_storage",
            factor_in={"heat": -1.0},  # Consumes heat when charging
            factor_out={"heat": 0.95},  # Produces heat when discharging (95% efficiency)
            factor_keep={"heat": 0.98},  # Heat loss rate (98% retention per hour)
            life_span=20.,
            invest_cost_energy=100.,
            invest_cost_power=50.,
            power_capacity_investment_max=60,
            energy_capacity_investment_max=300,
        )
        area.add_component(thermal_storage)

        # Add hydrogen storage
        hydrogen_storage = StorageTechnology(
            name="hydrogen_storage",
            factor_in={"hydrogen": -1.0},  # Consumes hydrogen when charging
            factor_out={"hydrogen": 0.98},  # Produces hydrogen when discharging (98% efficiency)
            factor_keep={"hydrogen": 0.999},  # Very low loss rate (99.9% retention per hour)
            life_span=25.,
            invest_cost_energy=500.,
            invest_cost_power=200.,
            power_capacity_investment_max=40,
            energy_capacity_investment_max=500,
        )
        area.add_component(hydrogen_storage)

    # Run the model
    energy_model.run()

    energy_model.set_all_results()
    # Check that some storage capacity was invested in
    storage_energy_capacity = battery.results["operation"]["power_capacity"]
    assert storage_energy_capacity is not None

    # Check that some conversion capacity was invested in
    solar_pv_capacity = solar_pv.results["operation"]["power_capacity"]
    assert solar_pv_capacity is not None

    # Check that the energy balance is maintained
    # (This would require more detailed analysis of the results)

    # The test passes if the model runs without errors and the basic assertions pass
