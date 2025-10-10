import pytest
import polars as pl
from pommes_craft.core.model import EnergyModel
from pommes_craft.core.component import Component
from pommes_craft.components.area import Area
from pommes_craft.components.demand import Demand
from pommes_craft.components.storage_technology import StorageTechnology
from pommes_craft.components.transport_technology import TransportTechnology
from pommes_craft.components.link import Link


def test_component_initialization():
    """Test that a component can be initialized with the expected attributes."""
    # Create a model for the component
    model = EnergyModel(
        name="test_component_model",
        hours=list(range(12)),  # A simple 12-hour period for faster tests
        year_ops=[2020],  # Single operational year
        year_invs=[2020],  # Single investment year
        year_decs=[2040],  # Single decommissioning year
        modes=["normal"],  # Single operation mode
        resources=["electricity"],  # A basic resource
    )

    # Create a component within the model context
    with model.context():
        area = Area("test_area")

    # Verify the component attributes
    assert area.name == "test_area"
    assert area.model == model


def test_component_area_relationship():
    """Test the relationship between components and areas."""
    # Create a model
    model = EnergyModel(
        name="test_area_relationship_model",
        hours=list(range(12)),
        year_ops=[2020],
        year_invs=[2020],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity"],
    )

    # Create an area and a component within the area
    with model.context():
        area = Area("test_area")

        # Create a demand component
        demand = Demand(
            name="test_demand",
            resource="electricity",
            demand=pl.DataFrame([
                {"hour": h, "year_op": 2020, "demand": 100}
                for h in model.hours
            ]),
        )

        # Add the demand to the area
        area.add_component(demand)

    # Verify the relationship
    assert demand.area == area
    assert "test_demand" in area.components
    assert area.components["test_demand"] == demand


def test_component_link_relationship():
    """Test the relationship between components and links."""
    # Create a model
    model = EnergyModel(
        name="test_link_relationship_model",
        hours=list(range(12)),
        year_ops=[2020],
        year_invs=[2020],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity"],
    )

    # Create two areas and a link between them
    with model.context():
        area1 = Area("area1")
        area2 = Area("area2")

        # Create a link between the areas
        link = Link("link", area1, area2)

        # Create a transport technology
        transport = TransportTechnology(
            name="test_transport",
            resource="electricity",
            life_span=20.,
            invest_cost=100.,
            power_capacity_investment_max=50.,
        )

        # Add the transport technology to the link
        link.add_transport_technology(transport)

    # Verify the relationship
    assert transport.link == link
    assert "test_transport" in link.technologies
    assert link.technologies["test_transport"] == transport


def test_component_process_attribute_input():
    """Test that attribute input is processed correctly."""
    # Create a model
    model = EnergyModel(
        name="test_process_attribute_model",
        hours=list(range(12)),
        year_ops=[2020, 2030],
        year_invs=[2020, 2030],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity", "heat"],
    )

    # Create a component
    with model.context():
        area = Area("test_area")

        # Test processing a single value input
        single_value = 100
        df_single = area.process_attribute_input("test_attr", single_value)
        assert isinstance(df_single, pl.DataFrame)
        assert "test_attr" in df_single.columns
        assert df_single["test_attr"].item() == single_value

        # Test processing a dictionary input with resource keys
        dict_value = {"electricity": 0.9, "heat": 0.8}
        df_dict = area.process_attribute_input("test_attr", dict_value, ["resource"])
        assert isinstance(df_dict, pl.DataFrame)
        assert "test_attr" in df_dict.columns
        assert "resource" in df_dict.columns
        assert df_dict.filter(pl.col("resource") == "electricity")["test_attr"].item() == 0.9
        assert df_dict.filter(pl.col("resource") == "heat")["test_attr"].item() == 0.8

        # Test processing a nested dictionary input with resource and year_op keys
        nested_dict_value = {
            "electricity": {2020: 0.9, 2030: 0.95},
            "heat": {2020: 0.8, 2030: 0.85}
        }
        df_nested = area.process_attribute_input("test_attr", nested_dict_value, ["resource", "year_op"])
        assert isinstance(df_nested, pl.DataFrame)
        assert "test_attr" in df_nested.columns
        assert "resource" in df_nested.columns
        assert "year_op" in df_nested.columns
        assert df_nested.filter((pl.col("resource") == "electricity") & (pl.col("year_op") == 2020))[
                   "test_attr"].item() == 0.9
        assert df_nested.filter((pl.col("resource") == "electricity") & (pl.col("year_op") == 2030))[
                   "test_attr"].item() == 0.95
        assert df_nested.filter((pl.col("resource") == "heat") & (pl.col("year_op") == 2020))["test_attr"].item() == 0.8
        assert df_nested.filter((pl.col("resource") == "heat") & (pl.col("year_op") == 2030))[
                   "test_attr"].item() == 0.85


def test_component_generate_component_table():
    """Test that component tables can be generated correctly."""
    # Create a model
    model = EnergyModel(
        name="test_generate_table_model",
        hours=list(range(12)),
        year_ops=[2020],
        year_invs=[2020],
        year_decs=[2040],
        modes=["normal"],
        resources=["electricity"],
    )

    # Create a component
    with model.context():
        area = Area("test_area")

        # Create a storage technology with various attributes
        storage = StorageTechnology(
            name="test_storage",
            factor_in={"electricity": -1.0},
            factor_out={"electricity": 0.9},
            factor_keep={"electricity": 0.99},
            dissipation=0.01,
            life_span=20.,
            finance_rate=0.05,
            invest_cost_energy=200.,
            invest_cost_power=100.,
        )

        area.add_component(storage)

    # Generate a component table for a specific attribute
    attr_names = ["factor_in"]
    parameters = {"storage_factor_in": {"index": ["resource", "year_op"],
                                        "index_input": {"resource": ["electricity"], "year_op": [2020]}}}
    index_input, table = storage.generate_component_table(storage, attr_names, parameters)

    # Verify the table
    assert isinstance(table, pl.DataFrame)
    assert "factor_in" in table.columns
    assert "resource" in table.columns
    assert "year_op" in table.columns
    assert table.filter(pl.col("resource") == "electricity")["factor_in"].item() == -1.0
