from typing import Dict, Union, Optional

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class Carbon(Component):
    """Carbon-related parameters for the energy system model."""

    area_indexed = False
    link_indexed = False
    prefix = "carbon_"
    own_index = None

    attr_index_dict = {
        "goal": ["year_op"],
        "tax": ["year_op"],
    }

    discount_rate: pl.DataFrame
    year_ref: pl.DataFrame
    planning_step: pl.DataFrame

    def __init__(
            self,
            name: str,
            goal: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
            tax: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
    ):
        """Initialize a carbon component.

        Args:
            name: Name of the carbon component
            goal: Carbon emission reduction goals by year
            tax: Carbon tax rates by year
        """
        super().__init__(name)

        # Get all parameters from locals() without 'self' and 'name'
        params = {
            k: v
            for k, v in locals().items()
            if k in self.attr_index_dict
        }

        # Process each attribute using the generic method
        for attr_name, attr_value in params.items():
            other_columns = self.attr_index_dict.get(attr_name, [])
            setattr(
                self,
                attr_name,
                self.process_attribute_input(attr_name, attr_value, other_columns),
            )
