import pytest
import polars as pl
from pathlib import Path
from pommes_craft.core.model import EnergyModel
from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand
from pommes_craft.components.storage_technology import StorageTechnology
from pommes_craft.components.time_step_manager import TimeStepManager
from pommes_craft.components.economic_hypothesis import EconomicHypothesis
from pommes_craft import LoadShedding


def test_energy_model_initialization():
    """Test that an EnergyModel can be initialized with the expected attributes."""
    # Create a basic energy model
    model = EnergyModel(
        name="test_model",
        hours=list(range(12)),  # A simple 12-hour period for faster tests
        year_ops=[2020],  # Single operational year
        year_invs=[2020],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        modes=["normal"],  # Single operation mode
        resources=["electricity"],  # A basic resource
    )

    # Verify the model attributes
    assert model.name == "test_model"
    assert model.hours == list(range(12))
    assert model.year_ops == [2020]
    assert model.year_invs == [2020]
    assert model.year_decs == [2040]
    assert model.modes == ["normal"]
    assert model.resources == ["electricity"]


def test_energy_model_context():
    """Test that the context manager works correctly."""
    model = EnergyModel(
        name="test_context_model",
        hours=list(range(12)),
        year_ops=[2020],
        year_invs=[2020],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity"],
    )

    # Use the context manager to create components
    with model.context():
        area = Area("test_area")

    # Verify that the component was registered with the model
    assert area in model.components
    assert "test_area" in model.areas
    assert model.areas["test_area"] == area


def test_energy_model_create_component():
    """Test that components can be created and registered with the model."""
    model = EnergyModel(
        name="test_create_component_model",
        hours=list(range(12)),
        year_ops=[2020],
        year_invs=[2020],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity"],
    )

    # Create a component using the create_component method
    with model.context():
        # Use TimeStepManager
        # Note: The model parameter is handled by the EnergyModel.create_component method
        # and passed to the Component.__init__ method
        time_step_manager = TimeStepManager(
            name="test_time_step_manager",
            time_step_duration=1.0,
            operation_year_duration=8760.0
        )

    # Verify that the component was created and registered
    assert time_step_manager in model.components
    assert isinstance(time_step_manager, TimeStepManager)

    # Check that the component has the correct attributes
    assert time_step_manager.name == "test_time_step_manager"
    assert time_step_manager.model == model


def test_energy_model_register_component():
    """Test that components can be registered with the model."""
    model = EnergyModel(
        name="test_register_component_model",
        hours=list(range(12)),
        year_ops=[2020],
        year_invs=[2020],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity"],
    )

    # Create a component within the model context
    with model.context():
        time_step_manager = TimeStepManager(
            name="test_time_step_manager",
            time_step_duration=1.0,
            operation_year_duration=8760.0
        )

    # Verify that the component was registered
    assert time_step_manager in model.components
    assert isinstance(time_step_manager, TimeStepManager)
    assert time_step_manager.model == model


def test_energy_model_run():
    """Test that the model can be run."""
    # Create a simple model with an area and a demand
    model = EnergyModel(
        name="test_run_model",
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

        # Add a storage technology to meet the demand
        battery = StorageTechnology(
            name="battery",
            factor_in={"electricity": -1.0},
            factor_out={"electricity": 1.0},
            factor_keep={"electricity": 1.0},
            life_span=20.,
            invest_cost_energy=100.,
            invest_cost_power=50.,
            power_capacity_investment_max=200,
            energy_capacity_investment_max=1000,
        )

        area.add_component(battery)

    # Run the model
    try:
        model.run()
        # If we get here, the model ran without errors
        assert True
    except Exception as e:
        # If we get an exception, the test fails
        assert False, f"Model run failed with exception: {e}"


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

    # Try to get some results
    model.set_all_results()
    from_model = model.get_results("operation", "power")
    from_component = load_shedding.results['operation']['power']
    # If we get here, the results were retrieved without errors
    assert from_model is not None
    assert from_component is not None
    assert from_component.shape[0] == from_model.shape[0]
    assert all(c in from_model.columns for c in from_component.columns)
