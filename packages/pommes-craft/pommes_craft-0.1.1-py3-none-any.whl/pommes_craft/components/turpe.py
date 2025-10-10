from typing import Dict, Optional, Union

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class Turpe(Component):
    """French electricity transmission and distribution tariff (TURPE) component."""
    area_indexed = False
    link_indexed = False
    prefix = "turpe_"
    own_index = None

    attr_index_dict = {
        "calendar": ["hour", "year_op"],
        "fixed_cost": ["hour_type", "year_op"],
        "variable_cost": ["hour_type", "year_op"],
    }
    # Class-level type annotations for all attributes that will be set dynamically
    calendar: pl.DataFrame
    fixed_cost: pl.DataFrame
    variable_cost: pl.DataFrame

    def __init__(
            self,
            name: str,
            calendar: Optional[Union[str, Dict[int, str], Dict[int, Dict[int, str]], pl.DataFrame]] = np.nan,
            fixed_cost: Optional[Union[float, Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame]] = 0.,
            variable_cost: Optional[Union[float, Dict[str, float], Dict[str, Dict[int, float]], pl.DataFrame]] = 0.
    ):
        """Initialize a TURPE component.

        Args:
            name: Name of the TURPE component
            calendar: Calendar of hour types by hour and year
            fixed_cost: Fixed costs by hour type and year
            variable_cost: Variable costs by hour type and year
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
            attr_df = self.process_attribute_input(attr_name, attr_value, other_columns)
            setattr(
                self,
                attr_name,
                attr_df,
            )
