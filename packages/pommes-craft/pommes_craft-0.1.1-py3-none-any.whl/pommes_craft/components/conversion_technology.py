from typing import Dict, Optional, Union

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class ConversionTechnology(Component):
    """Technology that converts between energy carriers."""
    area_indexed = True
    link_indexed = False
    prefix = "conversion_"
    own_index = "conversion_tech"

    attr_index_dict = {
        "factor": ["resource", "year_op"],
        "annuity_perfect_foresight": ["year_inv"],
        "annuity_cost": ["year_dec", "year_inv"],
        "availability": ["hour", "year_op"],
        "early_decommissioning": ["year_inv"],
        "emission_factor": ["year_op"],
        "end_of_life": ["year_inv"],
        "finance_rate": ["year_inv"],
        "fixed_cost": ["year_op"],
        "invest_cost": ["year_inv"],
        "variable_cost": ["year_op"],
        "life_span": ["year_inv"],
        "power_capacity_max": ["year_op"],
        "power_capacity_min": ["year_op"],
        "power_capacity_investment_max": ["year_inv"],
        "power_capacity_investment_min": ["year_inv"],
        "max_yearly_production": ["year_op"],
        "must_run": ["year_op"],
        "ramp_down": ["year_op"],
        "ramp_up": ["year_op"],
    }
    # Class-level type annotations for all attributes that will be set dynamically
    factor: pl.DataFrame
    annuity_perfect_foresight: pl.DataFrame
    annuity_cost: pl.DataFrame
    availability: pl.DataFrame
    early_decommissioning: pl.DataFrame
    emission_factor: pl.DataFrame
    end_of_life: pl.DataFrame
    finance_rate: pl.DataFrame
    fixed_cost: pl.DataFrame
    invest_cost: pl.DataFrame
    variable_cost: pl.DataFrame
    life_span: pl.DataFrame
    power_capacity_max: pl.DataFrame
    power_capacity_min: pl.DataFrame
    power_capacity_investment_max: pl.DataFrame
    power_capacity_investment_min: pl.DataFrame
    max_yearly_production: pl.DataFrame
    must_run: pl.DataFrame
    ramp_down: pl.DataFrame
    ramp_up: pl.DataFrame

    def __init__(
        self,
        name: str,
        factor: Union[Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame],
        annuity_perfect_foresight: Optional[
            Union[bool, Dict[int, bool], pl.DataFrame]
        ] = False,
        annuity_cost: Optional[
            Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]
        ] = np.nan,
        availability: Optional[
            Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]
        ] = np.nan,
        early_decommissioning: Optional[
            Union[bool, Dict[int, bool], pl.DataFrame]
        ] = False,
        emission_factor: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        end_of_life: Optional[Union[int, Dict[int, int], pl.DataFrame]] = 0,
        finance_rate: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        fixed_cost: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        invest_cost: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        variable_cost: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        life_span: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        power_capacity_max: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        power_capacity_min: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        power_capacity_investment_max: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        power_capacity_investment_min: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        max_yearly_production: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        must_run: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        ramp_down: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        ramp_up: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
    ):
        """Initialize a conversion technology component.

        Args:
            name: Name of the conversion technology
            factor: Conversion factors between energy carriers by resource and year
            annuity_perfect_foresight: Whether to use perfect foresight for annuity calculation
            annuity_cost: Annualized investment cost by year of decommissioning and investment
            availability: Availability factor by hour and year
            early_decommissioning: Whether early decommissioning is allowed
            emission_factor: Emission factors by year
            end_of_life: End of life year by investment year
            finance_rate: Finance rate by investment year
            fixed_cost: Fixed operation and maintenance costs by year
            invest_cost: Investment cost by year
            variable_cost: Variable operation and maintenance costs by year
            life_span: Technical lifetime by investment year
            power_capacity_max: Maximum power capacity by year
            power_capacity_min: Minimum power capacity by year
            power_capacity_investment_max: Maximum power capacity investment by year
            power_capacity_investment_min: Minimum power capacity investment by year
            max_yearly_production: Maximum yearly production by year
            must_run: Minimum power output as fraction of capacity by year
            ramp_down: Maximum ramp down rate as fraction of capacity by year
            ramp_up: Maximum ramp up rate as fraction of capacity by year
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
