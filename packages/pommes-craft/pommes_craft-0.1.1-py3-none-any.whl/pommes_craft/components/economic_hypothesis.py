from typing import Dict, Union, Optional

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class EconomicHypothesis(Component):
    """Economic hypothesis parameters for the model."""
    area_indexed = False
    link_indexed = False
    prefix = ""
    own_index = None

    attr_index_dict = {
        "discount_rate": ["year_op"],
        "year_ref": [],
        "planning_step": [],
    }

    discount_rate: pl.DataFrame
    year_ref: pl.DataFrame
    planning_step: pl.DataFrame

    def __init__(
            self,
            name: str,
            discount_rate: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 0.,
            year_ref: Optional[Union[int, Dict, pl.DataFrame]] = 2020,
            planning_step: Optional[int] = np.nan,
    ):
        """Initialize an economic hypothesis component.

        Args:
            name: Name of the economic hypothesis component
            discount_rate: Discount rate by year for economic calculations
            year_ref: Reference year for present value calculations
            planning_step: Planning step size in years
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
