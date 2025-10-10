import pytest
import polars as pl
import numpy as np
from pommes_craft.components.conversion_technology import ConversionTechnology


def test_single_value_inputs(energy_model):
    """Test ConversionTechnology with single value inputs."""
    # Create a technology with scalar values for all attributes
    with energy_model.context():
        tech = ConversionTechnology(
            name="nuke",
            factor={
                "electricity": 1.0,
            },
            annuity_perfect_foresight=True,
            annuity_cost=100.0,
            availability=0.95,
            early_decommissioning=False,
            emission_factor=0.5,
            end_of_life=20,
            finance_rate=0.07,
            fixed_cost=50.0,
            invest_cost=1000.0,
            variable_cost=10.0,
            life_span=25.0,
            power_capacity_max=100.0,
            power_capacity_min=20.0,
            power_capacity_investment_max=150.0,
            power_capacity_investment_min=0.0,
            max_yearly_production=800.0,
            must_run=0.1,
            ramp_down=0.2,
            ramp_up=0.3,
        )

    # Check that all attributes are polars DataFrames
    assert isinstance(tech.factor, pl.DataFrame)
    assert isinstance(tech.annuity_perfect_foresight, pl.DataFrame)
    assert isinstance(tech.annuity_cost, pl.DataFrame)

    # Check that DataFrames have the correct structure
    # For factor attribute
    assert set(tech.factor.columns) == {"resource", "year_op", "factor"}
    assert tech.factor.shape[0] == 3 # one for each year_op
    assert tech.factor["factor"][0] == 1.0

    # For annuity_perfect_foresight attribute
    assert set(tech.annuity_perfect_foresight.columns) == {
        "year_inv",
        "annuity_perfect_foresight",
    }
    assert tech.annuity_perfect_foresight["annuity_perfect_foresight"][0] is True

    # For annuity_cost attribute with two index columns
    assert set(tech.annuity_cost.columns) == {"year_dec", "year_inv", "annuity_cost"}
    assert tech.annuity_cost["annuity_cost"][0] == 100.0


def test_dict_inputs(energy_model):
    """Test ConversionTechnology with dictionary inputs."""
    # Create dictionary inputs
    factor_dict = {"electricity": {2020: 1., 2030: 1., 2040: 1.}, "methane": {2020: -1.82, 2030: -1.82, 2040: -1.82}}
    annuity_dict = {2020: True, 2030: False, 2040: True}

    # Nested dictionary for annuity_cost (two index columns)
    annuity_cost_dict = {
        2040: {2020: 100.0, 2030: 130.0, 2040: 120.0},
    }

    # Other dictionaries
    emission_factor_dict = {2020: 0.5, 2030: 0.4, 2040: 0.3}
    variable_cost_dict = {2020: 10.0, 2030: 9.5, 2040: 9.0}

    with energy_model.context():
        # Create a technology with dict inputs for some attributes
        tech = ConversionTechnology(
            name="ccgt",
            factor=factor_dict,
            annuity_perfect_foresight=annuity_dict,
            annuity_cost=annuity_cost_dict,
            emission_factor=emission_factor_dict,
            variable_cost=variable_cost_dict,
            # Default single values for other attributes
            availability=0.95,
            early_decommissioning=False,
            end_of_life=20,
            finance_rate=0.07,
            fixed_cost=50.0,
            invest_cost=1000.0,
            life_span=25.0,
            power_capacity_max=100.0,
            power_capacity_min=20.0,
            power_capacity_investment_max=150.0,
            power_capacity_investment_min=0.0,
            max_yearly_production=800.0,
            must_run=0.1,
            ramp_down=0.2,
            ramp_up=0.3,
        )

    # Check that dictionaries were converted to DataFrames correctly
    # Factor attribute (first level dict)
    assert tech.factor.shape[0] == len(factor_dict) * 3
    assert set(tech.factor["resource"].to_list()) == set(factor_dict.keys())
    for resource, f_by_year in factor_dict.items():
        for year_op, value in f_by_year.items():
            factor_value = tech.factor.filter((pl.col("resource") == resource) & (pl.col("year_op") == year_op))["factor"][0]
            assert factor_value == value

    # Annuity_perfect_foresight attribute (first level dict)
    assert tech.annuity_perfect_foresight.shape[0] == len(annuity_dict)
    assert set(tech.annuity_perfect_foresight["year_inv"].to_list()) == set(
        annuity_dict.keys()
    )

    # Annuity_cost attribute (nested dict)
    # Should have 6 rows (one for each year_dec, year_inv combination)
    assert tech.annuity_cost.shape[0] == 3
    # Check a specific value
    filtered_df = tech.annuity_cost.filter(
        (pl.col("year_dec") == 2040) & (pl.col("year_inv") == 2030)
    )
    assert filtered_df["annuity_cost"][0] == 130.0
