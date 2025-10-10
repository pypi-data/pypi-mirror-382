from typing import Optional, Union, Dict

import numpy as np
import polars as pl

from pommes_craft.core.component import Component


class LoadShedding(Component):
    """
    A class representing load shedding for a resource in the simulation.

    This class is used to represent the load shedding for a specific resource in
    a given area. It encapsulates data attributes such as the
    load shedding cost and capacity. The input data for demand or other
    parameters can be provided as floats, dictionaries, or dataframes,
    which are processed and stored appropriately.

    :ivar area_indexed: Indicates if the component is indexed by area.
    :type area_indexed: bool
    :ivar link_indexed: Indicates if the component is indexed by link.
    :type link_indexed: bool
    :ivar prefix: Represents the prefix for the component.
    :type prefix: str
    :ivar own_index: Represents the unique index for the component.
    :type own_index: Optional[int]
    :ivar attr_index_dict: A dictionary mapping attributes to lists of
        index names they depend on.
    :type attr_index_dict: dict
    """
    area_indexed = True
    link_indexed = False
    resource_indexed = True
    prefix = "load_shedding_"
    own_index = None

    attr_index_dict = {
        "cost": ["year_op"],
        "max_capacity": ["year_op"],
    }

    def __init__(
            self, name: str,
            resource: str,
            cost: Optional[Union[float, Dict[int, float], pl.DataFrame]] = 1000.,
            max_capacity: Optional[Union[float, Dict[int, float], pl.DataFrame]] = np.nan,
    ):
        """
        Initializes an instance of the class with specified parameters. This constructor
        sets up the attributes related to the resource, demands, load shedding, and
        spillage configurations. It includes processing inputs and preparing them
        for further use by adding the necessary resource reference.

        :param name: Name of the instance.
        :type name: str
        :param resource: Resource associated with this instance.
        :type resource: str
        :param cost: Cost associated with load shedding, can be a single
            value, a dictionary of costs indexed by time, or a DataFrame.
        :type cost: Optional[Union[float, Dict[int, float], pl.DataFrame]]
        :param max_capacity: Maximum allowable capacity for load shedding,
            can be a single value, a dictionary indexed by time, or a DataFrame.
        :type max_capacity: Optional[Union[float, Dict[int, float], pl.DataFrame]]
        """
        super().__init__(name)
        self.resource = resource

        params = {
            k: v
            for k, v in locals().items()
            if k in self.attr_index_dict
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
