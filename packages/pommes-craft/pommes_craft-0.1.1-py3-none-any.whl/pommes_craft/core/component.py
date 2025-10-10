# pommes_craft/core/components.py
import inspect
import math
from abc import ABC, abstractmethod
import logging
import numpy as np
import polars as pl
import xarray as xr
from typing import get_type_hints, get_origin, get_args, Union
# from model import EnergyModel
from pommes_craft.core.model_context import ModelContext
import pommes_craft

# Set up a logger for this module
logger = logging.getLogger(__name__)


def _validate_dict_keys(attr_name, input_value, other_columns, model_dimensions):
    """
    Validate dictionary keys against model dimensions.

    Args:
        attr_name: The name of the attribute
        input_value: Dictionary input
        other_columns: List of column names for additional dimensions
        model_dimensions: Dictionary of valid dimension values
    """
    first_dim = other_columns[0]

    # Check if the dictionary keys are valid for the first dimension
    if first_dim in model_dimensions and model_dimensions[first_dim]:
        valid_keys = set(model_dimensions[first_dim])
        input_keys = set(input_value.keys())
        invalid_keys = input_keys - valid_keys

        if invalid_keys:
            raise ValueError(
                f"Invalid {first_dim} values in {attr_name} input: {invalid_keys}. "
                f"Valid values are: {valid_keys}"
            )

    # Check nested dictionaries if present
    if any(isinstance(v, dict) for v in input_value.values()):
        second_dim = other_columns[1] if len(other_columns) > 1 else None
        if second_dim and second_dim in model_dimensions and model_dimensions[second_dim]:
            valid_keys = set(model_dimensions[second_dim])

            for key, nested_dict in input_value.items():
                if isinstance(nested_dict, dict):
                    nested_keys = set(nested_dict.keys())
                    invalid_nested_keys = nested_keys - valid_keys

                    if invalid_nested_keys:
                        raise ValueError(
                            f"Invalid {second_dim} values in nested dict for {first_dim}={key}: "
                            f"{invalid_nested_keys}. Valid values are: {valid_keys}"
                        )


def _process_single_value_input(attr_name, input_value, other_columns, model_dimensions):
    """
    Process a single value input into a DataFrame.

    Args:
        attr_name: The name of the attribute
        input_value: Single value input (float, int, bool)
        other_columns: List of column names for additional dimensions
        model_dimensions: Dictionary of valid dimension values

    Returns:
        pl.DataFrame: DataFrame with the single value expanded across all dimension combinations
    """
    # Create rows for each combination of dimension values
    rows = []

    # Helper function to create cartesian product of model dimensions
    def build_rows(current_row, dims_to_process):
        if not dims_to_process:
            current_row[attr_name] = input_value
            rows.append(current_row.copy())
            return

        current_dim = dims_to_process[0]
        remaining_dims = dims_to_process[1:]

        for val in model_dimensions[current_dim]:
            current_row[current_dim] = val
            build_rows(current_row, remaining_dims)

    build_rows({}, other_columns)
    return pl.DataFrame(rows)


def _process_dict_input(attr_name, input_value, other_columns, model_dimensions):
    """
    Process a dictionary input into a DataFrame.

    Args:
        attr_name: The name of the attribute
        input_value: Dictionary mapping first dimension values to attribute values
        other_columns: List of column names for additional dimensions
        model_dimensions: Dictionary of valid dimension values

    Returns:
        pl.DataFrame: DataFrame with the dictionary expanded across remaining dimensions
    """
    first_dim = other_columns[0]
    remaining_dims = other_columns[1:]

    # Start with the values provided by the user
    rows = []
    for key, value in input_value.items():
        # For each remaining dimension, create entries for all values from the model
        base_row = {first_dim: key, attr_name: value}

        def expand_row(current_row, dims_to_process):
            if not dims_to_process:
                rows.append(current_row.copy())
                return

            current_dim = dims_to_process[0]
            remaining = dims_to_process[1:]

            for val in model_dimensions[current_dim]:
                current_row[current_dim] = val
                expand_row(current_row, remaining)

        expand_row(base_row, remaining_dims)

    return pl.DataFrame(rows)


def _process_nested_dict_input(attr_name, input_value, other_columns, model_dimensions):
    """
    Process a nested dictionary input into a DataFrame.

    Args:
        attr_name: The name of the attribute
        input_value: Dictionary of dictionaries mapping first and second dimension values to attribute values
        other_columns: List of column names for additional dimensions
        model_dimensions: Dictionary of valid dimension values

    Returns:
        pl.DataFrame: DataFrame with the nested dictionary expanded across remaining dimensions
    """
    first_dim = other_columns[0]
    second_dim = other_columns[1]
    remaining_dims = other_columns[2:] if len(other_columns) > 2 else []

    rows = []
    for first_key, nested_dict in input_value.items():
        for second_key, value in nested_dict.items():
            base_row = {first_dim: first_key, second_dim: second_key, attr_name: value}

            def expand_row(current_row, dims_to_process):
                if not dims_to_process:
                    rows.append(current_row.copy())
                    return

                current_dim = dims_to_process[0]
                remaining = dims_to_process[1:]

                for val in model_dimensions[current_dim]:
                    current_row[current_dim] = val
                    expand_row(current_row, remaining)

            expand_row(base_row, remaining_dims)

    return pl.DataFrame(rows)


class Component(ABC):
    """Abstract base class for all energy system components."""
    area_indexed = False
    link_indexed = False
    resource_indexed = False
    prefix = ""
    attr_index_dict = {}
    own_index = None

    def __init__(self, name: str, model: "pommes_craft.core.model.EnergyModel" = None, **kwargs):
        """
        Initialize a component with optional model reference and validation parameters.

        Args:
            name: Component name
            model: EnergyModel instance (optional if in model context)
            **kwargs: Additional parameters that may require model validation
                      (e.g., hours, year_op, regions)
        """
        self.name = name
        self.resource = None
        self.results = None

        # Get model from parameter or context
        self._model = model
        if self._model is None:
            try:
                self._model = ModelContext.get_current_model()
            except RuntimeError:
                raise ValueError(
                    "EnergyModel must be provided (either directly or via context) "
                    "when creating components with parameters requiring validation"
                )
        self._model.register_component(self)

    @property
    def model(self) -> "pommes_craft.core.model.EnergyModel":
        """Get the associated energy model."""
        return self._model

    @property
    def area(self):
        """
        Get the area that contains this component.

        Returns:
            Area: The area containing this component, or None if not in any area
        """
        areas_in_model = self.model.areas.values()
        component_area = None
        for area in areas_in_model:
            if self in area.components.values():
                component_area = area
                break
        return component_area

    @property
    def link(self):
        """
        Get the link that contains this component.

        Returns:
            Link: The link containing this component, or None if not in any link
        """
        links_in_model = self.model.links.values()
        component_link = None
        for link in links_in_model:
            if self in link.technologies.values():
                component_link = link
                break
        return component_link

    def process_attribute_input(
            self, attr_name: str, input_value, other_columns=None
    ) -> pl.DataFrame:
        """
        Process attribute input into a standardized polars DataFrame format.

        Args:
            attr_name: The name of the attribute (will be a column in the DataFrame)
            input_value: Input value in one of several formats:
                - Single value (float, int, bool)
                - Dict mapping other_columns[0] values to attr_name values
                - Dict of dicts mapping other_columns[0] values to dicts mapping other_columns[1] values to attr_name values
                - pl.DataFrame (already in correct format)
            other_columns: List of column names for additional dimensions (e.g., ["year", "region"])

        Returns:
            pl.DataFrame: Standardized DataFrame with attr_name column and other specified columns
        """
        if other_columns is None:
            other_columns = ["year", "region"]  # Default dimensions, adjust as needed

        # Get model dimensions for validation and expansion
        model_dimensions = self._get_model_dimensions(other_columns)

        # Process based on input type
        if isinstance(input_value, pl.DataFrame):
            return self._process_dataframe_input(attr_name, input_value, other_columns)
        elif not isinstance(input_value, dict):
            return _process_single_value_input(attr_name, input_value, other_columns, model_dimensions)
        elif not any(isinstance(v, dict) for v in input_value.values()):
            # Validate dictionary keys
            _validate_dict_keys(attr_name, input_value, other_columns, model_dimensions)
            return _process_dict_input(attr_name, input_value, other_columns, model_dimensions)
        else:
            # Validate dictionary keys
            _validate_dict_keys(attr_name, input_value, other_columns, model_dimensions)
            return _process_nested_dict_input(attr_name, input_value, other_columns, model_dimensions)

    def _get_model_dimensions(self, other_columns):
        """
        Get dimension values from the model for each column.

        Args:
            other_columns: List of column names for additional dimensions

        Returns:
            dict: Dictionary mapping column names to their valid values from the model
        """
        model_dimensions = {}
        for col in other_columns:
            # Try to get dimension values from the model
            model_attr = f"{col}s"

            if hasattr(self.model, model_attr):
                model_dimensions[col] = getattr(self.model, model_attr)
            else:
                # Default to a single placeholder value if dimension not in model
                model_dimensions[col] = [0]

        return model_dimensions

    def _process_dataframe_input(self, attr_name, input_value, other_columns):
        """
        Process an input that is already a polars DataFrame.

        Args:
            attr_name: The name of the attribute
            input_value: Input DataFrame
            other_columns: List of column names for additional dimensions

        Returns:
            pl.DataFrame: Validated DataFrame
        """
        # Check if the DataFrame contains the attr_name column
        if attr_name not in input_value.columns:
            raise ValueError(f"Input DataFrame must contain the '{attr_name}' column")

        # Check if the DataFrame contains all required other_columns
        missing_cols = [col for col in other_columns if col not in input_value.columns]
        if missing_cols:
            raise ValueError(f"Input DataFrame is missing required columns: {missing_cols}")

        # Validate that values in dimension columns match the model's valid values
        for col in other_columns:
            # Get the valid values for this dimension from the model
            model_attr = f"{col}s"

            if hasattr(self.model, model_attr):
                valid_values = set(getattr(self.model, model_attr))
                df_values = set(input_value[col].unique())
                invalid_values = df_values - valid_values

                if invalid_values:
                    raise ValueError(
                        f"Invalid {col} values in DataFrame input for: {invalid_values}. "
                        f"Valid values are: {valid_values}"
                    )

        return input_value

    @classmethod
    def generate_class_parameters(cls):
        """
        Generate parameter definitions for this component class.

        This method introspects the class definition to determine types and default values
        for all attributes defined in attr_index_dict.

        Returns:
            tuple: (parameters, component_index_groups)
                - parameters: Dictionary of parameter definitions
                - component_index_groups: Dictionary mapping index keys to lists of attribute names
        """
        # Get the constructor signature to extract default values
        signature = inspect.signature(cls.__init__)

        # Get type hints from the class
        type_hints = get_type_hints(cls.__init__)

        # Create index groups for this component type
        component_index_groups = {}

        parameters = {}

        # Iterate through attributes in attr_index_dict
        for attr_name, indexes in cls.attr_index_dict.items():
            param_name = f"{cls.prefix}{attr_name}"

            # Extract type information from type hints
            python_type, fill_value = extract_type_and_default(
                attr_name,
                type_hints.get(attr_name),
                signature.parameters.get(attr_name)
            )

            # Construct complete index list
            all_indexes = indexes.copy() if indexes else []
            if cls.own_index is not None:
                all_indexes = [cls.own_index] + all_indexes
            if cls.area_indexed:
                all_indexes = ["area"] + all_indexes
            if cls.link_indexed:
                all_indexes = ["link"] + all_indexes
            if cls.resource_indexed:
                all_indexes = ['resource'] + all_indexes

            # Create a string key from all indexes to group similar parameters
            index_key = "_".join(all_indexes)

            # Group parameters by their index structure
            if index_key not in component_index_groups:
                component_index_groups[index_key] = []
            component_index_groups[index_key].append(attr_name)

            # Create parameter definition
            parameters[param_name] = {
                # File will be assigned later after all groups are identified
                "column": attr_name,
                "type": python_type_to_param_type(python_type),
                "fill": fill_value,
                "index_input": all_indexes,
                "cls_name": cls.__name__,
                "index_key": index_key  # Temporary key to help with file assignments
            }
        return parameters, component_index_groups

    def generate_component_table(self, component, attr_names, parameters):
        """
        Generate a table for a component with the specified attributes.

        Args:
            component: The component to generate a table for
            attr_names: List of attribute names to include in the table
            parameters: Dictionary of parameter definitions

        Returns:
            tuple: (index_input, dataframe)
                - index_input: List of index column names
                - dataframe: Generated DataFrame with component data, or None if no data
        """
        logger.debug(f"Generating CSV file for {component.name} of class {component.__class__}")
        # Check if this component has any of the needed attributes
        has_any_attr = False
        for attr_name in attr_names:
            if hasattr(component, attr_name) and isinstance(getattr(component, attr_name), pl.DataFrame):
                has_any_attr = True
                break

        if not has_any_attr:
            return None

        # Get first attribute info to determine index structure
        index_input = parameters[component.prefix + attr_names[0]]["index_input"]

        if not index_input:
            return index_input, self._generate_component_no_index(attr_names)
        else:
            return index_input, self._generate_component_with_index(attr_names, index_input)

    def _generate_component_no_index(self, attr_names):
        """
        Generate a table for a component without index dimensions.

        This method creates a single-row DataFrame containing values for all
        specified attributes, along with any required index columns.

        Args:
            attr_names: List of attribute names to include in the table

        Returns:
            pl.DataFrame: DataFrame with component data
        """
        row_data = {}

        # Add component's own index if needed
        if self.own_index:
            row_data[self.own_index] = self.name

        # Add area index if needed
        if self.area_indexed and self.area:
            row_data["area"] = self.area.name

        # Add link index if needed
        if self.link_indexed and self.link:
            row_data["link"] = self.link.name

        # Add link index if needed
        if self.resource_indexed and self.resource:
            row_data["resource"] = self.resource


        # Add values from all attributes
        for attr_name in attr_names:
            if hasattr(self, attr_name) and isinstance(getattr(self, attr_name), pl.DataFrame):
                df = getattr(self, attr_name)
                row_data[attr_name] = df[attr_name][0]

        return pl.DataFrame([row_data])

    def _generate_component_with_index(self, attr_names, index_input):
        """
        Generate a table for a component with index dimensions.

        This method creates a DataFrame containing values for all specified attributes,
        properly indexed by the component's index dimensions.

        Args:
            attr_names: List of attribute names to include in the table
            index_input: List of index column names

        Returns:
            pl.DataFrame: DataFrame with component data, or None if no data
        """
        # Case with index - start with a base dataframe containing just the index columns
        base_df = None
        for attr_name in attr_names:
            if hasattr(self, attr_name) and isinstance(getattr(self, attr_name), pl.DataFrame):
                df = getattr(self, attr_name)
                # Filter to only include columns that are actually in the DataFrame
                existing_cols = [col for col in index_input if col in df.columns]
                if existing_cols:
                    base_df = df.select(existing_cols).unique()
                    break

        if base_df is None:
            return None

        # Add component's own name as index column if not already there
        if self.own_index and self.own_index not in base_df.columns:
            base_df = base_df.with_columns(pl.lit(self.name).alias(self.own_index))

        # Add area index if needed
        if self.area_indexed and "area" not in base_df.columns and self.area:
            base_df = base_df.with_columns(pl.lit(self.area.name).alias("area"))

        # Add link index if needed
        if self.link_indexed and "link" not in base_df.columns and self.link:
            base_df = base_df.with_columns(pl.lit(self.link.name).alias("link"))

        # Add resource index if needed
        if self.resource_indexed and "resource" not in base_df.columns and self.resource:
            base_df = base_df.with_columns(pl.lit(self.resource).alias("resource"))

        # Join all value columns from all attribute dataframes
        for attr_name in attr_names:
            if hasattr(self, attr_name) and isinstance(getattr(self, attr_name), pl.DataFrame):
                df = getattr(self, attr_name)
                join_index = [c for c in df.columns if c in index_input]
                # Join with the base dataframe
                if len(join_index) > 0:
                    base_df = base_df.join(df, on=join_index, how="left")
                else:
                    base_df = pl.concat([base_df, df], how='horizontal')

        return base_df

    def set_results(self):
        """
        Access the optimization results related to this component from the model's solution.

        This method filters the results from the linopy_model based on the component's prefix
        and indexes (own_index, area_indexed, etc.).

        Returns:
            xarray.Dataset: A dataset containing only the results related to this component
        """
        # Check if the model has been solved
        if self.model.linopy_model is None or not hasattr(self.model.linopy_model, 'solution'):
            raise ValueError("Model has not been solved yet. Run model.run() first.")

        # Get the solution dataset
        solution = self.model.linopy_model.solution

        # Filter variables that start with the component's prefix
        if self.prefix:
            # Create a dictionary to store filtered results
            filtered_results = {
                "operation": {},
                "planning": {}
            }

            # Iterate through all variables in the solution
            for var_name, var_data in solution.data_vars.items():
                # Check if the variable name starts with the component's prefix
                if self.prefix in var_name:
                    cols_to_drop = []
                    filtered_data = var_data
                    # If the component has an own_index, filter by the component's name
                    if self.own_index and self.own_index in var_data.dims:
                        filtered_data = filtered_data.sel({self.own_index: self.name})
                        cols_to_drop.append(self.own_index)
                    # If the component is area_indexed, filter by the area's name
                    if self.area_indexed and "area" in var_data.dims and self.area:
                        filtered_data = filtered_data.sel({"area": self.area.name})
                        cols_to_drop.append("area")
                    # If the component is link_indexed, filter by the link's name
                    if self.link_indexed and "link" in var_data.dims and self.link:
                        filtered_data = filtered_data.sel({"link": self.link.name})
                        cols_to_drop.append("link")
                    # If the component is resource_indexed, filter by the resource's name
                    if self.resource_indexed and "resource" in var_data.dims and self.resource:
                        filtered_data = filtered_data.sel({"resource": self.resource})
                        cols_to_drop.append("resource")

                    filtered_data = pl.from_pandas(filtered_data.to_dataframe(),
                                                   include_index=True).drop(cols_to_drop).rename({var_name: 'value'})
                    if "hour" in filtered_data.columns:
                        filtered_data = filtered_data.with_columns([
                            (pl.datetime(pl.col("year_op"), 1, 1) +
                             pl.duration(hours=pl.col("hour")))
                            .alias("datetime")
                        ])
                        filtered_data = filtered_data.sort("datetime")

                    if 'operation' in var_name:
                        var_name = var_name.replace('operation_', '').replace(self.prefix, '')
                        filtered_results['operation'][var_name] = filtered_data
                    if 'planning' in var_name:
                        var_name = var_name.replace('planning_', '').replace(self.prefix, '')
                        filtered_results['planning'][var_name] = filtered_data

            self.results = filtered_results


def python_type_to_param_type(python_type):
    """
    Convert Python type to parameter type string.

    Args:
        python_type: Python type (bool, int, float, etc.)

    Returns:
        str: Parameter type string ('bool', 'int64', 'float64', etc.)
    """
    type_map = {
        bool: "bool",
        int: "int64",
        float: "float64",
        str: "str",
        object: "str"
    }

    return type_map.get(python_type, "float64")  # Default to float64


def extract_type_and_default(attr_name, type_hint, param_info):
    """
    Extract Python type and default value from type hint and parameter info.

    Args:
        attr_name: Name of the attribute
        type_hint: Type hint from the class
        param_info: Parameter information from inspect.signature

    Returns:
        tuple: (python_type, default_value)
    """
    # Default fallbacks
    default_python_type = object
    default_value = "nan"

    # Extract default value from parameter info
    if param_info and param_info.default is not inspect.Parameter.empty:
        default_value = param_info.default

    # If no type hint, return defaults
    if not type_hint:
        return default_python_type, default_value

    # Process Optional[...] and Union[...] types
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is Union:
        # Handle Union types (including Optional which is Union[type, None])
        # Extract the non-None, non-DataFrame types
        python_types = [arg for arg in args if arg is not type(None) and arg is not pl.DataFrame]

        if python_types:
            # Use the first type in the union as the main type
            python_type = python_types[0]

            # Extract base type if it's Dict or other container
            if get_origin(python_type) is dict:
                value_type = get_args(python_type)[1]  # Dict[key_type, value_type]
                return value_type, default_value

            return python_type, default_value

    # Default type if we couldn't determine it
    return default_python_type, default_value


def format_default_value(value):
    """
    Format default value for YAML output.

    Args:
        value: Default value from parameter

    Returns:
        Formatted value for YAML
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, (int, float)):
        # Check for NaN using both numpy and math (for robustness)
        if (hasattr(np, 'isnan') and np.isnan(value)) or (hasattr(math, 'isnan') and math.isnan(value)):
            return "nan"  # Return string "nan" without the dot
        return value
    else:
        return str(value)
