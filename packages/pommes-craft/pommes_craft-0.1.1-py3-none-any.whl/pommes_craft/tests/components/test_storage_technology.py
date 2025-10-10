import polars as pl
import pytest
from pommes_craft.components.storage_technology import StorageTechnology


def test_resource_single_value_inputs(energy_model):
    """Test StorageTechnology with Dict[str, float] inputs (resource keys)."""
    # Define test parameters with correct keys based on attr_index_dict
    # For attributes indexed by ["resource", "year_op"]
    factor_in = {"electricity": 0.9}
    factor_keep = {"electricity": 0.95}
    factor_out = {"electricity": 0.9}

    # For attributes indexed by ["year_op"]
    dissipation = 0.01 # Using a sample year_op
    fixed_cost_energy = 5.0
    fixed_cost_power = 3.0

    # For attributes indexed by ["year_inv"]
    life_span = 20  # Using a sample year_inv
    finance_rate = 0.05
    annuity_perfect_foresight = True
    invest_cost_energy = 200.0
    invest_cost_power = 100.0
    end_of_life = False
    early_decommissioning = False
    energy_capacity_investment_min = 0
    energy_capacity_investment_max = 1000
    power_capacity_investment_min = 0
    power_capacity_investment_max = 500

    # For attributes indexed by ["year_dec", "year_inv"]
    # Using sample years for both indices
    annuity_cost_energy = 100.0
    annuity_cost_power = 50.0
    with energy_model.context():
        # Create StorageTechnology instance with a name
        st = StorageTechnology(
            name="battery_storage",
            factor_in=factor_in,
            factor_keep=factor_keep,
            factor_out=factor_out,
            dissipation=dissipation,
            life_span=life_span,
            finance_rate=finance_rate,
            annuity_perfect_foresight=annuity_perfect_foresight,
            annuity_cost_energy=annuity_cost_energy,
            annuity_cost_power=annuity_cost_power,
            fixed_cost_energy=fixed_cost_energy,
            fixed_cost_power=fixed_cost_power,
            invest_cost_energy=invest_cost_energy,
            invest_cost_power=invest_cost_power,
            end_of_life=end_of_life,
            early_decommissioning=early_decommissioning,
            energy_capacity_investment_min=energy_capacity_investment_min,
            energy_capacity_investment_max=energy_capacity_investment_max,
            power_capacity_investment_min=power_capacity_investment_min,
            power_capacity_investment_max=power_capacity_investment_max,
        )

    # Test attribute values
    assert st.name == "battery_storage"
    resource = "electricity"
    year_op = 2020  # Sample operation year
    year_inv = 2020  # Sample investment year
    year_dec = 2040  # Sample decommissioning year

    # For dataframe attributes, we need to check specific values
    # Attributes indexed by ["resource", "year_op"]
    assert (
        st.factor_in.filter(
            pl.col("resource") == resource, pl.col("year_op") == year_op
        )
        .select("factor_in")
        .item()
        == factor_in[resource]
    )
    assert (
        st.factor_keep.filter(
            pl.col("resource") == resource, pl.col("year_op") == year_op
        )
        .select("factor_keep")
        .item()
        == factor_keep[resource]
    )
    assert (
        st.factor_out.filter(
            pl.col("resource") == resource, pl.col("year_op") == year_op
        )
        .select("factor_out")
        .item()
        == factor_out[resource]
    )

    # Attributes indexed by ["year_op"]
    assert (
        st.dissipation.filter(pl.col("year_op") == year_op).select("dissipation").item()
        == dissipation
    )
    assert (
        st.fixed_cost_energy.filter(pl.col("year_op") == year_op).select("fixed_cost_energy").item()
        == fixed_cost_energy
    )
    assert (
        st.fixed_cost_power.filter(pl.col("year_op") == year_op).select("fixed_cost_power").item()
        == fixed_cost_power
    )

    # Attributes indexed by ["year_inv"]
    assert (
        st.life_span.filter(pl.col("year_inv") == year_inv).select("life_span").item()
        == life_span
    )
    assert (
        st.finance_rate.filter(pl.col("year_inv") == year_inv).select("finance_rate").item()
        == finance_rate
    )
    assert (
        st.annuity_perfect_foresight.filter(pl.col("year_inv") == year_inv)
        .select("annuity_perfect_foresight")
        .item()
        == annuity_perfect_foresight
    )
    assert (
        st.invest_cost_energy.filter(pl.col("year_inv") == year_inv)
        .select("invest_cost_energy")
        .item()
        == invest_cost_energy
    )
    assert (
        st.invest_cost_power.filter(pl.col("year_inv") == year_inv)
        .select("invest_cost_power")
        .item()
        == invest_cost_power
    )
    assert (
        st.end_of_life.filter(pl.col("year_inv") == year_inv).select("end_of_life").item()
        == end_of_life
    )
    assert (
        st.early_decommissioning.filter(pl.col("year_inv") == year_inv)
        .select("early_decommissioning")
        .item()
        == early_decommissioning
    )
    assert (
        st.energy_capacity_investment_min.filter(pl.col("year_inv") == year_inv)
        .select("energy_capacity_investment_min")
        .item()
        == energy_capacity_investment_min
    )
    assert (
        st.energy_capacity_investment_max.filter(pl.col("year_inv") == year_inv)
        .select("energy_capacity_investment_max")
        .item()
        == energy_capacity_investment_max
    )
    assert (
        st.power_capacity_investment_min.filter(pl.col("year_inv") == year_inv)
        .select("power_capacity_investment_min")
        .item()
        == power_capacity_investment_min
    )
    assert (
        st.power_capacity_investment_max.filter(pl.col("year_inv") == year_inv)
        .select("power_capacity_investment_max")
        .item()
        == power_capacity_investment_max
    )

    # Attributes indexed by ["year_dec", "year_inv"]
    assert (
        st.annuity_cost_energy.filter(
            pl.col("year_dec") == year_dec, pl.col("year_inv") == year_inv
        )
        .select("annuity_cost_energy")
        .item()
        == annuity_cost_energy
    )
    assert (
        st.annuity_cost_power.filter(
            pl.col("year_dec") == year_dec, pl.col("year_inv") == year_inv
        )
        .select("annuity_cost_power")
        .item()
        == annuity_cost_power
    )


def test_resource_year_dict_inputs(energy_model):
    """Test StorageTechnology with Dict[str, Dict[int, float]] inputs (resource keys with year subkeys)."""
    # Extract dimensions from the energy model to ensure consistency
    years_ops = energy_model.year_ops  # [2020, 2030, 2040]
    years_invs = energy_model.year_invs  # [2020, 2030, 2040]
    years_decs = energy_model.year_decs  # [2040]
    resources = energy_model.resources  # ["electricity"]

    # Create dictionaries for each variable based on their index requirements

    # Variables indexed by [resource, year_op]
    factor_in = {resource: {year: 0.9 + 0.01 * i
                            for i, year in enumerate(years_ops)}
                 for resource in resources}

    factor_keep = {resource: {year: 0.95 + 0.01 * i
                              for i, year in enumerate(years_ops)}
                   for resource in resources}

    factor_out = {resource: {year: 0.85 + 0.01 * i
                             for i, year in enumerate(years_ops)}
                  for resource in resources}

    # Variables indexed by [year_op]
    dissipation = {year: 0.01 + 0.005 * i for i, year in enumerate(years_ops)}
    fixed_cost_energy = {year: 5.0 + 1.0 * i for i, year in enumerate(years_ops)}
    fixed_cost_power = {year: 10.0 + 2.0 * i for i, year in enumerate(years_ops)}

    # Variables indexed by [year_inv]
    annuity_perfect_foresight = {year: True for i, year in enumerate(years_invs)}
    finance_rate = {year: 0.05 + 0.01 * i for i, year in enumerate(years_invs)}
    invest_cost_energy = {year: 100.0 + 10.0 * i for i, year in enumerate(years_invs)}
    invest_cost_power = {year: 500.0 + 50.0 * i for i, year in enumerate(years_invs)}
    life_span = {year: 20.0 + 2.0 * i for i, year in enumerate(years_invs)}
    end_of_life = {year: 10 + 5 * i for i, year in enumerate(years_invs)}
    early_decommissioning = {year: False for year in years_invs}
    energy_capacity_investment_min = {year: 0.0 for year in years_invs}
    energy_capacity_investment_max = {year: 1000.0 + 100.0 * i for i, year in enumerate(years_invs)}
    power_capacity_investment_min = {year: 0.0 for year in years_invs}
    power_capacity_investment_max = {year: 500.0 + 50.0 * i for i, year in enumerate(years_invs)}

    # Variables indexed by [year_dec, year_inv]
    annuity_cost_energy = {
        dec_year: {inv_year: 10.0 + i * 2.0 + j
                   for j, inv_year in enumerate(years_invs) if inv_year <= dec_year}
        for i, dec_year in enumerate(years_decs)
    }

    annuity_cost_power = {
        dec_year: {inv_year: 50.0 + i * 5.0 + j
                   for j, inv_year in enumerate(years_invs) if inv_year <= dec_year}
        for i, dec_year in enumerate(years_decs)
    }
    with energy_model.context():
        # Create StorageTechnology instance
        storage = StorageTechnology(
            name="pumped_hydro",
            factor_in=factor_in,
            factor_keep=factor_keep,
            factor_out=factor_out,
            dissipation=dissipation,
            life_span=life_span,
            finance_rate=finance_rate,
            annuity_perfect_foresight=annuity_perfect_foresight,
            annuity_cost_energy=annuity_cost_energy,
            annuity_cost_power=annuity_cost_power,
            fixed_cost_energy=fixed_cost_energy,
            fixed_cost_power=fixed_cost_power,
            invest_cost_energy=invest_cost_energy,
            invest_cost_power=invest_cost_power,
            end_of_life=end_of_life,
            early_decommissioning=early_decommissioning,
            energy_capacity_investment_min=energy_capacity_investment_min,
            energy_capacity_investment_max=energy_capacity_investment_max,
            power_capacity_investment_min=power_capacity_investment_min,
            power_capacity_investment_max=power_capacity_investment_max,
        )

    # Test attribute values
    assert storage.name == "pumped_hydro"
    # Test variables indexed by [resource, year_op]
    for resource in resources:
        for i, year in enumerate(years_ops):
            # For polars DataFrame attributes with resource and year_op indices
            assert storage.factor_in.filter(
                (pl.col("resource") == resource) & (pl.col("year_op") == year)
            ).select("factor_in").item() == pytest.approx(0.9 + 0.01 * i)

            assert storage.factor_keep.filter(
                (pl.col("resource") == resource) & (pl.col("year_op") == year)
            ).select("factor_keep").item() == pytest.approx(0.95 + 0.01 * i)

            assert storage.factor_out.filter(
                (pl.col("resource") == resource) & (pl.col("year_op") == year)
            ).select("factor_out").item() == pytest.approx(0.85 + 0.01 * i)

    # Test variables indexed by [year_op]
    for i, year in enumerate(years_ops):
        # For polars DataFrame attributes with year_op index
        assert storage.dissipation.filter(
            pl.col("year_op") == year
        ).select("dissipation").item() == pytest.approx(0.01 + 0.005 * i)

        assert storage.fixed_cost_energy.filter(
            pl.col("year_op") == year
        ).select("fixed_cost_energy").item() == pytest.approx(5.0 + 1.0 * i)

        assert storage.fixed_cost_power.filter(
            pl.col("year_op") == year
        ).select("fixed_cost_power").item() == pytest.approx(10.0 + 2.0 * i)

    # Test variables indexed by [year_inv]
    for i, year in enumerate(years_invs):
        # For polars DataFrame attributes with year_inv index
        assert storage.annuity_perfect_foresight.filter(
            pl.col("year_inv") == year
        ).select("annuity_perfect_foresight").item() == True

        assert storage.finance_rate.filter(
            pl.col("year_inv") == year
        ).select("finance_rate").item() == pytest.approx(0.05 + 0.01 * i)

        assert storage.invest_cost_energy.filter(
            pl.col("year_inv") == year
        ).select("invest_cost_energy").item() == pytest.approx(100.0 + 10.0 * i)

        assert storage.invest_cost_power.filter(
            pl.col("year_inv") == year
        ).select("invest_cost_power").item() == pytest.approx(500.0 + 50.0 * i)

        assert storage.life_span.filter(
            pl.col("year_inv") == year
        ).select("life_span").item() == pytest.approx(20.0 + 2.0 * i)

        assert storage.end_of_life.filter(
            pl.col("year_inv") == year
        ).select("end_of_life").item() == pytest.approx(10 + 5 * i)

        assert storage.early_decommissioning.filter(
            pl.col("year_inv") == year
        ).select("early_decommissioning").item() == False

        assert storage.energy_capacity_investment_min.filter(
            pl.col("year_inv") == year
        ).select("energy_capacity_investment_min").item() == 0.0

        assert storage.energy_capacity_investment_max.filter(
            pl.col("year_inv") == year
        ).select("energy_capacity_investment_max").item() == pytest.approx(1000.0 + 100.0 * i)

        assert storage.power_capacity_investment_min.filter(
            pl.col("year_inv") == year
        ).select("power_capacity_investment_min").item() == 0.0

        assert storage.power_capacity_investment_max.filter(
            pl.col("year_inv") == year
        ).select("power_capacity_investment_max").item() == pytest.approx(500.0 + 50.0 * i)

    # Test variables indexed by [year_dec, year_inv]
    for i, dec_year in enumerate(years_decs):
        for j, inv_year in enumerate(years_invs):
            if inv_year <= dec_year:
                # For polars DataFrame attributes with year_dec and year_inv indices
                assert storage.annuity_cost_energy.filter(
                    (pl.col("year_dec") == dec_year) & (pl.col("year_inv") == inv_year)
                ).select("annuity_cost_energy").item() == pytest.approx(10.0 + i * 2.0 + j)

                assert storage.annuity_cost_power.filter(
                    (pl.col("year_dec") == dec_year) & (pl.col("year_inv") == inv_year)
                ).select("annuity_cost_power").item() == pytest.approx(50.0 + i * 5.0 + j)
