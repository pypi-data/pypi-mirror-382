from typing import Dict, Optional, Union

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class StorageTechnology(Component):
    """Technology that stores energy for later use."""
    area_indexed = True
    link_indexed = False
    prefix = "storage_"
    own_index = "storage_tech"

    attr_index_dict = {
        "factor_in": ["resource", "year_op"],
        "factor_keep": ["resource", "year_op"],
        "factor_out": ["resource", "year_op"],
        "annuity_perfect_foresight": ["year_inv"],
        "annuity_cost_energy": ["year_dec", "year_inv"],
        "annuity_cost_power": ["year_dec", "year_inv"],
        "dissipation": ["year_op"],
        "early_decommissioning": ["year_inv"],
        "end_of_life": ["year_inv"],
        "finance_rate": ["year_inv"],
        "fixed_cost_energy": ["year_op"],
        "fixed_cost_power": ["year_op"],
        "invest_cost_energy": ["year_inv"],
        "invest_cost_power": ["year_inv"],
        "life_span": ["year_inv"],
        "energy_capacity_investment_max": ["year_inv"],
        "energy_capacity_investment_min": ["year_inv"],
        "power_capacity_investment_max": ["year_inv"],
        "power_capacity_investment_min": ["year_inv"],
    }
    # Class-level type annotations for all attributes that will be set dynamically
    factor_in: pl.DataFrame
    factor_keep: pl.DataFrame
    factor_out: pl.DataFrame
    annuity_perfect_foresight: pl.DataFrame
    annuity_cost_energy: pl.DataFrame
    annuity_cost_power: pl.DataFrame
    dissipation: pl.DataFrame
    early_decommissioning: pl.DataFrame
    end_of_life: pl.DataFrame
    finance_rate: pl.DataFrame
    fixed_cost_energy: pl.DataFrame
    fixed_cost_power: pl.DataFrame
    invest_cost_energy: pl.DataFrame
    invest_cost_power: pl.DataFrame
    life_span: pl.DataFrame
    energy_capacity_investment_max: pl.DataFrame
    energy_capacity_investment_min: pl.DataFrame
    power_capacity_investment_max: pl.DataFrame
    power_capacity_investment_min: pl.DataFrame

    def __init__(
        self,
        name: str,
        factor_in: Union[Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame],
        factor_keep: Union[Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame],
        factor_out: Union[Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame],
        annuity_perfect_foresight: Optional[
            Union[bool, Dict[int, bool], pl.DataFrame]
        ] = False,
        annuity_cost_energy: Optional[
            Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]
        ] = np.nan,
        annuity_cost_power: Optional[
            Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]
        ] = np.nan,
        dissipation: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        early_decommissioning: Optional[
            Union[bool, Dict[int, bool], pl.DataFrame]
        ] = False,
        emission_factor: Optional[
            Union[Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame]
        ] = 0.0,
        end_of_life: Optional[Union[int, Dict[int, int], pl.DataFrame]] = 0,
        finance_rate: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        fixed_cost_energy: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        fixed_cost_power: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        invest_cost_energy: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = 0.0,
        invest_cost_power: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        life_span: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        energy_capacity_investment_max: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        energy_capacity_investment_min: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        power_capacity_investment_max: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        power_capacity_investment_min: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
    ):
        """Initialize a storage technology component.

        Args:
            name: Name of the storage technology
            factor_in: Conversion factors for charging by resource and year
            factor_keep: Conversion factors for storage retention by resource and year
            factor_out: Conversion factors for discharging by resource and year
            annuity_perfect_foresight: Whether to use perfect foresight for annuity calculation
            annuity_cost_energy: Annualized investment cost for energy capacity by year of decommissioning and investment
            annuity_cost_power: Annualized investment cost for power capacity by year of decommissioning and investment
            dissipation: Energy dissipation rate by year
            early_decommissioning: Whether early decommissioning is allowed
            emission_factor: Emission factors by resource and year
            end_of_life: End of life year by investment year
            finance_rate: Finance rate by investment year
            fixed_cost_energy: Fixed operation and maintenance costs for energy capacity by year
            fixed_cost_power: Fixed operation and maintenance costs for power capacity by year
            invest_cost_energy: Investment cost for energy capacity by year
            invest_cost_power: Investment cost for power capacity by year
            life_span: Technical lifetime by investment year
            energy_capacity_investment_max: Maximum energy capacity investment by year
            energy_capacity_investment_min: Minimum energy capacity investment by year
            power_capacity_investment_max: Maximum power capacity investment by year
            power_capacity_investment_min: Minimum power capacity investment by year
        """
        super().__init__(name)

        # Get all parameters from locals() without 'self' and 'name'
        params = {
            k: v
            for k, v in locals().items()
            if k not in ("self", "name") and k in self.attr_index_dict
        }
        # Process each attribute using the generic method
        for attr_name, attr_value in params.items():
            other_columns = self.attr_index_dict.get(attr_name, [])
            setattr(
                self,
                attr_name,
                self.process_attribute_input(attr_name, attr_value, other_columns),
            )
