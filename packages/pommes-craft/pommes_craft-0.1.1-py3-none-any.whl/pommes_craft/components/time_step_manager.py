from typing import Dict, Union, Optional

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class TimeStepManager(Component):
    """Time step and calendar information for the model."""
    area_indexed = False
    link_indexed = False
    prefix = ""
    own_index = None

    attr_index_dict = {
        "time_step_duration": ["hour"],
        "operation_year_duration": ["year_op"],
    }

    time_step_duration: pl.DataFrame
    operation_year_duration: pl.DataFrame

    def __init__(
            self,
            name: str,
            time_step_duration: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
            operation_year_duration: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
    ):
        """Initialize a time step manager component.

        Args:
            name: Name of the time step manager component
            time_step_duration: Duration of each time step in hours
            operation_year_duration: Duration of each operational year in days
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
