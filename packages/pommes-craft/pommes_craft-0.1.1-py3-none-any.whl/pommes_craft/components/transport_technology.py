from typing import Dict, Union, Optional

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class TransportTechnology(Component):
    """Technology for transporting energy between areas."""
    area_indexed = False
    link_indexed = True
    prefix = "transport_"
    own_index = "transport_tech"


    attr_index_dict = {
        "early_decommissioning": ["year_inv"],
        "end_of_life": ["year_inv"],
        "finance_rate": ["year_inv"],
        "fixed_cost": ["year_op"],
        "hurdle_costs": ["year_op"],
        "invest_cost": ["year_inv"],
        "life_span": ["year_inv"],
        "power_capacity_investment_max": ["year_inv"],
        "power_capacity_investment_min": ["year_inv"],
        "resource": [],
        "area_from": [],
        "area_to": [],
    }

    early_decommissioning: pl.DataFrame
    emission_factor: pl.DataFrame
    end_of_life: pl.DataFrame
    finance_rate: pl.DataFrame
    fixed_cost: pl.DataFrame
    hurdle_costs: pl.DataFrame
    invest_cost: pl.DataFrame
    life_span: pl.DataFrame
    power_capacity_investment_max: pl.DataFrame
    power_capacity_investment_min: pl.DataFrame

    def __init__(
        self,
        name: str,
        resource: str,
        early_decommissioning: Optional[
            Union[bool, Dict[int, bool], pl.DataFrame]
        ] = False,
        end_of_life: Optional[Union[int, Dict[int, int], pl.DataFrame]] = 0,
        finance_rate: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        fixed_cost: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        hurdle_costs: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        invest_cost: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.0,
        life_span: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        power_capacity_investment_max: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
        power_capacity_investment_min: Optional[
            Union[float, Dict[int, float], pl.DataFrame]
        ] = np.nan,
    ):
        """Initialize a transport technology component.

        Args:
            name: Name of the transport technology
            resource: Resource being transported
            early_decommissioning: Whether early decommissioning is allowed
            end_of_life: End of life year by investment year
            finance_rate: Finance rate by investment year
            fixed_cost: Fixed operation and maintenance costs by year
            hurdle_costs: Additional costs for using the transport technology by year
            invest_cost: Investment cost by year
            life_span: Technical lifetime by investment year
            power_capacity_investment_max: Maximum power capacity investment by year
            power_capacity_investment_min: Minimum power capacity investment by year
        """
        super().__init__(name)
        self.area_from = None
        self.area_to = None

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

    def register_link(self, link: 'Link'):
        """
        Register a link with this transport technology.

        If area_from or area_to attributes are None, initializes them as
        polars DataFrames with columns 'link' and 'area_from' or 'area_to'.

        Args:
            link: The Link object to be registered with this transport technology
        """

        area_from_df = pl.DataFrame({"link": [link.name], "area_from": [link.area_from.name]})
        if self.area_from is None:
            self.area_from = area_from_df
        else:
            self.area_from = self.area_from.vstack(area_from_df)

        area_to_df = pl.DataFrame({"link": [link.name], "area_to": [link.area_to.name]})
        if self.area_to is None:
            self.area_to = area_to_df
        else:
            self.area_to = self.area_to.vstack(area_to_df)
