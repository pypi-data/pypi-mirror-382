from typing import Dict, Optional, Union

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class NetImport(Component):
    """Component representing net import/export of resources to/from the system."""
    area_indexed = True
    link_indexed = False
    resource_indexed = True
    prefix = "net_import_"
    own_index = None

    attr_index_dict = {
        "emission_factor": ["hour", "year_op"],
        "import_price": ["hour", "year_op"],
        "max_yearly_energy_export": ["year_op"],
        "max_yearly_energy_import": ["year_op"],
        "total_emission_factor": ["hour", "year_op"],
    }
    # Class-level type annotations for all attributes that will be set dynamically
    emission_factor: pl.DataFrame
    import_price: pl.DataFrame
    max_yearly_energy_export: pl.DataFrame
    max_yearly_energy_import: pl.DataFrame
    total_emission_factor: pl.DataFrame


    def __init__(
        self,
        name: str,
        resource: str,
        emission_factor: Optional[Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]] = 0.,
        import_price:  Optional[Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]] = 0.,
        max_yearly_energy_export:  Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        max_yearly_energy_import:  Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
        total_emission_factor:  Optional[Union[float, Dict[int, float], Dict[int, Dict[int, float]], pl.DataFrame]] = 0.,
    ):
        """Initialize a net import component.

        Args:
            name: Name of the net import component
            resource: Resource being imported/exported
            emission_factor: Emission factor for the imported resource by hour and year
            import_price: Price of importing the resource by hour and year
            max_yearly_energy_export: Maximum yearly energy export by year
            max_yearly_energy_import: Maximum yearly energy import by year
            total_emission_factor: Total emission factor including upstream emissions by hour and year
        """
        super().__init__(name)
        self.resource = resource

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
            # add the resource column
            attr_df = attr_df.with_columns(resource=pl.lit(self.resource))
            setattr(
                self,
                attr_name,
                attr_df,
            )
