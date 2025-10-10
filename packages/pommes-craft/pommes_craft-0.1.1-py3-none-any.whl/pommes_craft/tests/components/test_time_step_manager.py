import pytest
import polars as pl
import numpy as np
from pommes_craft.core.model import EnergyModel
from pommes_craft.components.time_step_manager import TimeStepManager


def test_time_step_manager_single_value():
    """Test TimeStepManager with single value inputs."""
    # Create a model
    model = EnergyModel(
        name="test_time_step_model",
        hours=list(range(12)),  # A simple 12-hour period for faster tests
        year_ops=[2020, 2030],  # Two operational years
        year_invs=[2020],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        resources=["electricity"],  # A basic resource
    )

    # Create a TimeStepManager with single values
    time_step_duration = 1.0
    operation_year_duration = 8760.0  # Hours in a year

    with model.context():
        tsm = TimeStepManager(
            name="test_tsm",
            time_step_duration=time_step_duration,
            operation_year_duration=operation_year_duration,
        )

    # Verify the attributes
    # For time_step_duration (indexed by ["hour"])
    for hour in model.hours:
        assert tsm.time_step_duration.filter(
            (pl.col("hour") == hour)
        ).select("time_step_duration").item() == time_step_duration

    # For operation_year_duration (indexed by ["year_op", "mode"])
    for year_op in model.year_ops:
        assert tsm.operation_year_duration.filter(
            (pl.col("year_op") == year_op)
        ).select("operation_year_duration").item() == operation_year_duration


def test_time_step_manager_dict_by_year():
    """Test TimeStepManager with dictionary inputs by year."""
    # Create a model
    model = EnergyModel(
        name="test_time_step_model",
        hours=list(range(2)),  # A simple 12-hour period for faster tests
        year_ops=[2020, 2030],  # Two operational years
        year_invs=[2020],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        modes=["normal"],  # Single operation mode
        resources=["electricity"],  # A basic resource
    )

    # Create a TimeStepManager with dictionary values by hour
    time_step_duration = {0: 1.0, 1: 0.5}
    # and by year
    operation_year_duration = {2020: 8760.0, 2030: 4380.0}

    with model.context():
        tsm = TimeStepManager(
            name="test_tsm",
            time_step_duration=time_step_duration,
            operation_year_duration=operation_year_duration,
        )

    # For time_step_duration (indexed by ["hour"])
    for hour in model.hours:
        assert tsm.time_step_duration.filter(
            (pl.col("hour") == hour)
        ).select("time_step_duration").item() == time_step_duration[hour]

    # For operation_year_duration (indexed by ["year_op", "mode"])
    for year_op in model.year_ops:
        assert tsm.operation_year_duration.filter(
            (pl.col("year_op") == year_op)
        ).select("operation_year_duration").item() == operation_year_duration[year_op]


def test_time_step_manager_dataframe_input():
    """Test TimeStepManager with DataFrame inputs."""
    # Create a model
    model = EnergyModel(
        name="test_time_step_model",
        hours=list(range(12)),  # A simple 12-hour period for faster tests
        year_ops=[2020, 2030],  # Two operational years
        year_invs=[2020],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        modes=["normal", "peak"],  # Multiple operation modes
        resources=["electricity"],  # A basic resource
    )

    # Create DataFrame inputs
    time_step_duration = pl.DataFrame([
        {"hour": hour, "time_step_duration": 1.0 / (i + 1)}
        for i, hour in enumerate(model.hours)
    ])

    operation_year_duration = pl.DataFrame([
        {"year_op": year_op,
         "operation_year_duration": 8760.0 / (i + 1)} for i, year_op in enumerate(model.year_ops)
    ])

    with model.context():
        tsm = TimeStepManager(
            name="test_tsm",
            time_step_duration=time_step_duration,
            operation_year_duration=operation_year_duration,
        )

    assert tsm.time_step_duration.equals(time_step_duration)
    assert tsm.operation_year_duration.equals(operation_year_duration)
