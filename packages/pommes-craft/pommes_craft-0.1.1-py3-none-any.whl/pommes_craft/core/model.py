# pommes_craft/core/model.py
import logging
import numpy as np
import polars as pl
from pathlib import Path
from typing import Dict, Optional, Type, Any, Sequence
from pommes_craft import studies_path
from pommes_craft.core.component import Component
from pommes_craft.core.model_context import ModelContext
from pommes.model.data_validation.dataset_check import check_inputs
from pommes.io.build_input_dataset import (
    build_input_parameters,
    read_config_file,
)
from pommes.model.build_model import build_model

# Set up a logger for this module
logger = logging.getLogger(__name__)


class EnergyModel:
    """Main class for creating and solving POMMES energy system models."""


    def __init__(self,
                 name: str = "energy_model",
                 folder: Optional[Path] = None,
                 hours: Optional[Sequence[int]] = None,
                 year_ops: Optional[Sequence[int]] = None,
                 year_invs: Optional[Sequence[int]] = None,
                 year_decs: Optional[Sequence[int]] = None,
                 modes: Optional[Sequence[str]] = None,
                 resources: Optional[Sequence[str]] = None,
                 hour_types: Optional[Sequence[str]] = None,
                 add_modules: Optional[Dict[str, bool]] = None,
                 pre_process: Optional[Dict[str, Any]] = None,
                 solver_name: Optional[str] = "highs",
                 solver_options: Optional[Dict[str, str]] = None,
):
        """Initialize a new energy system model with all key attributes.

        Args:
            name: Name of the model
            hours: Operational hours for the model
            year_ops: Operational years for the model
            year_invs: Investment years for the model
            year_decs: Decommissioning years for the model
            modes: Operational modes for the model
            resources: Resource types available in the model
            add_modules: Optional dictionary to enable/disable specific modules
            pre_process: Optional dictionary containing preprocessing configurations

        """
        self.name = name
        logger.info(f"Creating new EnergyModel: '{name}' with {len(hours) if hours else 0} hours, "
                    f"{len(year_ops) if year_ops else 0} operational years, "
                    f"{len(year_invs) if year_invs else 0} investment years, "
                    f"{len(resources) if resources else 0} resources")


        if folder is None:
            self.folder = studies_path / self.name
        else:
            self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)
        self.solver_name = solver_name
        if solver_options is None:
            self.solver_options = {}
        else:
            self.solver_options = solver_options

        # Initialize core attributes with provided values or empty lists
        self.hours = list(hours) if hours is not None else []
        self.year_ops = list(year_ops) if year_ops is not None else []
        self.year_invs = list(year_invs) if year_invs is not None else []
        self.year_decs = list(year_decs) if year_decs is not None else []
        self.modes = list(modes) if modes is not None else []
        self.resources = list(resources) if resources is not None else []
        self.hour_types = list(hour_types) if hour_types is not None else []

        # add_modules will be set when generating the POMMES model
        self.add_modules = None
        if add_modules is not None:
            # Update the default dict with provided values
            self.add_modules.update(add_modules)

        # Default pre_process configuration
        default_pre_process = {
            'annuity_computation': {
                'combined': {
                    'combined_annuity_cost': {
                        'invest_cost': 'combined_invest_cost',
                        'finance_rate': 'combined_finance_rate',
                        'life_span': 'combined_life_span'
                    }
                },
                'conversion': {
                    'conversion_annuity_cost': {
                        'invest_cost': 'conversion_invest_cost',
                        'finance_rate': 'conversion_finance_rate',
                        'life_span': 'conversion_life_span'
                    }
                },
                'transport': {
                    'transport_annuity_cost': {
                        'invest_cost': 'transport_invest_cost',
                        'finance_rate': 'transport_finance_rate',
                        'life_span': 'transport_life_span'
                    }
                },
                'storage': {
                    'storage_annuity_cost_power': {
                        'invest_cost': 'storage_invest_cost_power',
                        'finance_rate': 'storage_finance_rate',
                        'life_span': 'storage_life_span'
                    },
                    'storage_annuity_cost_energy': {
                        'invest_cost': 'storage_invest_cost_energy',
                        'finance_rate': 'storage_finance_rate',
                        'life_span': 'storage_life_span'
                    }
                }
            },
            'discount_factor': {
                'discount_rate': 'discount_rate',
                'year_ref': 'year_ref'
            }
        }

        # Use provided pre_process or default configuration
        self.pre_process = default_pre_process
        if pre_process is not None:
            # Update with provided values
            self.pre_process.update(pre_process)

        # Component collections
        self.components = []  # Registry of all components as a list
        self.components_by_cls = {}  # Registry of all components by class
        self.areas = {}
        self.links = {}
        self._model_built = False

        # POMMES model attributes

        self.linopy_model = None
        self.config = {
            'config': {
                'solver': self.solver_name,
                'solver_options': self.solver_options,
            },
            'coords': {},
            'add_modules': None,
            'pre_process': self.pre_process,
            "input": {
                "path": None,
            }
        }
        self.parameter_tables = {}

    def context(self):
        """Return a context manager for this model."""
        return ModelContext(self)

    def create_component(self, component_class: Type[Component], name: str, **kwargs) -> Component:
        """
        Factory method to create a component linked to this model.

        Args:
            component_class: Component class to instantiate
            name: Name for the new component
            **kwargs: Additional parameters to pass to the component constructor

        Returns:
            The created component instance
        """
        component = component_class(name, model=self, **kwargs)
        return self.register_component(component)

    def register_component(self, component: Component) -> Component:
        """
        Register an existing component with this model.

        Args:
            component: Component instance to register

        Returns:
            The registered component
        """

        try:
            # Set model reference if not already set 
            if component.model is None:
                component._model = self
            elif component.model != self:
                logger.error(f"Component '{component.name}' already belongs to different model")
                raise ValueError(f"Component '{component.name}' already belongs to a different model")

            self.components.append(component)

            class_name = component.__class__.__name__
            if class_name not in self.components_by_cls:
                self.components_by_cls[class_name] = []
            self.components_by_cls[class_name].append(component)

            if class_name == "Area":
                if component.name not in self.areas:
                    self.areas[component.name] = component
                else:
                    logger.error(f"Area '{component.name}' already exists in model {self.name}")
                    raise ValueError(f"Duplicate area name: {component.name}")

            elif class_name == "Link":
                if component.name not in self.links:
                    self.links[component.name] = component

            logger.debug(f"Registered component: {component.name} of type {class_name} "
                         f"(total {class_name} components: {len(self.components_by_cls[class_name])})")
            return component
        except Exception as e:
            logger.error(f"Error registering component '{component.name}': {str(e)}")
            raise

    def to_pommes_model(self, output_dir='.'):
        """
        Export the energy model to POMMES configuration files.

        This method generates the necessary configuration files (config.yaml and tables)
        based on the components registered in the energy model.

        Parameters
        ----------
        output_dir : str, optional
            Directory where the output files will be saved, by default '.'

        Returns
        -------
        dict
            Dictionary containing the paths to the generated files
        """
        try:
            self._set_add_modules()
            self._add_coords_for_indexed_components()
            self._generate_component_parameters()
            self._add_generic_coords()

        except Exception as e:
            logger.error(f"Error exporting model '{self.name}' to POMMES configuration: {str(e)}")
            raise

    def _add_generic_coords(self):
        """
        Add generic coordinates to the model configuration.

        This method adds standard coordinates like mode, resource, hour, year_op, etc.
        to the model configuration based on the model's attributes.
        """
        coords_to_add = {
            'mode': {'type': 'str', 'attr': 'modes'},
            'resource': {'type': 'str', 'attr': 'resources'},
            'hour_type': {'type': 'str', 'attr': 'hour_types'},
            'hour': {'type': 'int64', 'attr': 'hours', 'conditional': True},
            'year_op': {'type': 'int', 'attr': 'year_ops', 'conditional': True},
            'year_inv': {'type': 'int', 'attr': 'year_invs', 'conditional': True},
            'year_dec': {'type': 'int', 'attr': 'year_decs', 'conditional': True}
        }

        # Add coordinates using the dictionary and getattr
        for coord_name, config_options in coords_to_add.items():
            attr_value = getattr(self, config_options['attr'])

            # Skip if conditional and attribute is None or empty
            if config_options.get('conditional', False) and not attr_value:
                continue

            # Add to config
            self.config['coords'][coord_name] = {
                'type': config_options['type'],
                'values': attr_value
            }

    def _add_coords_for_indexed_components(self):
        """
        Add coordinates for indexed components to the model configuration.

        This method identifies components with their own indices and adds them
        as coordinates to the model configuration.
        """
        component_conversion_dict = {
            component.own_index: component.__class__.__name__ for component in self.components if
            component.own_index is not None
        }
        # Add components with index
        for k, v in component_conversion_dict.items():
            components = [c for c in self.components if c.__class__.__name__ == v]
            self.config['coords'][k] = {
                'type': 'str',
                'values': list(set([component.name for component in components]))
            }

    def _set_add_modules(self):
        """
        Activates and configures the default add_module settings.

        This method initializes and activates the default configuration for
        various modules by setting their enabled state. Each module has a
        specific functionality, and this method ensures that all are activated
        by default.

        :return: A dictionary containing the default configuration settings
            for the 'add_modules' with their activation states (True).
        :rtype: dict
        """
        # Default add_module configuration (all modules enabled)
        self.add_modules = {
            'combined': any([c.__class__.__name__ == "CombinedTechnology" for c in self.components]),
            'conversion': any([c.__class__.__name__ == "ConversionTechnology" for c in self.components]),
            'carbon': any([c.__class__.__name__ == "Carbon" for c in self.components]),
            'transport': any([c.__class__.__name__ == "TransportTechnology" for c in self.components]),
            'turpe': any([c.__class__.__name__ == "Turpe" for c in self.components]),
            'storage': any([c.__class__.__name__ == "StorageTechnology" for c in self.components]),
            'net_import': any([c.__class__.__name__ == "NetImport" for c in self.components])
        }
        self.config['add_modules'] = self.add_modules

    def _generate_component_parameters(self):
        """
        Dynamically generate model parameters from component attributes by introspecting
        class definitions to determine types and default values.
        """
        logger.debug(f"Generating component parameters for {len(self.components)} components "
                     f"across {len(self.components_by_cls)} component types")


        parameters = {}
        # Track parameter groups by their index structure
        index_groups = {}

        # Track attributes by their file group
        file_attr_groups = {}  # file_name -> list of (param_name, attr_name, component_type)

        # Iterate through all components in the model
        for component_type_name, components in self.components_by_cls.items():
            if len(components) > 0:

                # Get a representative component and its class
                component_class = components[0].__class__
                params, component_index_groups = component_class.generate_class_parameters()
                parameters = parameters | params

                # Assign file names for each index group within this component type
                for index_key, attrs in component_index_groups.items():
                    # Create a descriptive file name based on prefix and index structure

                    if component_class.prefix != "":
                        file_name = f"{component_class.prefix}{index_key}.csv"
                    else:
                        file_name = f"{component_type_name.lower()}_{index_key}.csv"


                    # Store the file name for this index group
                    index_groups[(component_type_name, index_key)] = file_name

                    # Add all attributes to this file group
                    if file_name not in file_attr_groups:
                        file_attr_groups[file_name] = []

                    for attr in attrs:
                        file_attr_groups[file_name].append({
                            "param_name": f"{component_class.prefix}{attr}",
                            "attr_name": attr,
                            "component_type": component_type_name
                        })

        self.config["input"]["parameters"] = parameters

        # Assign file names to parameters
        for param_name, param_info in parameters.items():
            # Extract component type and index key
            for (component_type, index_key), file_name in index_groups.items():
                if (param_info["index_key"] == index_key) and (param_info["cls_name"] == component_type):
                    param_info["file"] = file_name
                    break

            # Clean up temporary key
            if "index_key" in param_info:
                del param_info["index_key"]

        # Now generate the tables for each group
        self._generate_tables_from_params(parameters, file_attr_groups)

    def _generate_tables_from_params(self, parameters, file_attr_groups):
        """
        Generate tables from parameters and component data.

        Args:
            parameters: Dictionary of parameter configurations
            file_attr_groups: Dictionary mapping file names to lists of attribute info
        """
        logger.debug(
            f"Generating tables from {len(parameters)} parameters across {len(file_attr_groups)} file groups")

        # Process each file group
        for file_name, attr_infos in file_attr_groups.items():

            if not attr_infos:
                continue
            comp_type = attr_infos[0]["component_type"]
            if comp_type not in self.components_by_cls:
                continue
            components = self.components_by_cls[comp_type]
            if not components:
                continue

            all_component_dfs = []
            attr_names = [attr['attr_name'] for attr in attr_infos]
            # Process each component
            for component in components:

                index_input, df = component.generate_component_table(component, attr_names, parameters)
                if df is not None:
                    all_component_dfs.append(df)

            # Combine all component dataframes and write to CSV
            if all_component_dfs:
                try:
                    combined_df = pl.concat(all_component_dfs).to_pandas()
                except Exception as e:
                    print(e)
                    for df in all_component_dfs:
                        print(df)
                if index_input:
                    combined_df = combined_df.set_index(index_input)

                self.parameter_tables[file_name] = combined_df
                logger.info(f"Generated table: {file_name} with {len(combined_df)} "
                            f"rows and {len(combined_df.columns)} columns")



    def run_pommes_model(self):
        """
        Run the POMMES optimization model using the current configuration.

        This method builds the input parameters, checks them, builds the model,
        and solves it using the specified solver and options.
        """
        logger.info(f"Running POMMES model: '{self.name}' from configuration in {self.folder}")
        p = build_input_parameters(self.config, self.parameter_tables)
        p = check_inputs(p)
        self.linopy_model = build_model(p)
        self.linopy_model.solve(solver_name=self.solver_name,
                                **self.solver_options
                                )
        logger.info(f"Model '{self.name}' solved successfully using solver: {self.solver_name}")


    def run(self):
        """
        Run the model by generating the POMMES configuration and solving the optimization problem.
        """
        self.to_pommes_model()
        self.run_pommes_model()

    def write_model(self, table_format='parquet'):
        """Save the model configuration and data tables to files.

        Args:
            table_format (str, optional): Format to save the data tables in. Defaults to 'parquet'.

        Returns:
            dict: Paths to generated files {'config': Path, 'tables': List[Path]}

        Raises:
            ValueError: If model configuration is invalid
            IOError: If there are file system related errors
            Exception: For other unexpected errors
        """
        import yaml
        generated_files = {'config_path': "", 'tables': []}

        try:
            logger.info(f"Saving model '{self.name}' to {self.folder} "
                        f"with {len(self.components)} components across {len(self.components_by_cls)} component types")

            generated_files['config_path'] = self.write_yaml()
            generated_files['tables'] = self.write_parameter_tables(table_format)

            logger.info(f"Model '{self.name}' saved successfully. Config: {generated_files['config_path']}, "
                        f"Generated {len(generated_files['tables'])} tables")

            return generated_files

        except (yaml.YAMLError, yaml.representer.RepresenterError) as e:
            logger.error(f"YAML serialization error while saving model '{self.name}': {str(e)}")
            raise ValueError(f"Failed to serialize model configuration: {str(e)}")
        except IOError as e:
            logger.error(f"I/O error while saving model '{self.name}': {str(e)}")
            raise IOError(f"Failed to write model files: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error while saving model '{self.name}': {str(e)}")
            raise

    def write_yaml(self):
        """
        Write the model configuration to a YAML file.

        Returns:
            str: Path to the generated config.yaml file
        """
        import yaml
        def represent_list(dumper, data):
            """Convert Python lists to YAML sequences with flow style."""
            return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)

        def represent_numpy_array(dumper, data):
            """Convert NumPy arrays to YAML sequences with flow style."""
            return dumper.represent_sequence('tag:yaml.org,2002:seq', data.tolist(), flow_style=True)

        def string_representer(dumper, data):
            """Represent strings with double quotes in YAML."""
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

        def nan_representer(dumper, _):
            """Represent NaN values as the string 'nan' in YAML."""
            return dumper.represent_scalar('tag:yaml.org,2002:str', 'nan')

        # Register the custom representers
        yaml.add_representer(list, represent_list)
        yaml.add_representer(np.ndarray, represent_numpy_array)
        yaml.add_representer(str, string_representer)
        yaml.add_representer(float('nan').__class__, nan_representer)

        # Write config.yaml
        config_path = self.folder / 'config.yaml'
        with config_path.open('w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        return config_path.__str__()

    def write_parameter_tables(self, table_format):
        """
        Write parameter tables to files in the specified format.

        Args:
            table_format (str): Format to save the tables in ('parquet' or 'csv')

        Returns:
            list: List of paths to the generated table files
        """
        # Create data subfolder it doesn't exist
        (self.folder / 'data').mkdir(parents=True, exist_ok=True)
        # Save parameter tables
        tables = []
        for file_name, df in self.parameter_tables.items():
            file_path = self.folder / 'data' / file_name.replace('.csv', f'.{table_format}')
            if table_format == 'parquet':
                df.to_parquet(file_path)
            else:
                df.to_csv(file_path, sep=';')
            tables.append(file_path.__str__())

        return tables

    def set_all_results(self):
        """
        set results for all components in the model.

        Returns:
            dict: A dictionary mapping component names to their results
        """
        if self.linopy_model is None or not hasattr(self.linopy_model, 'solution'):
            raise ValueError("Model has not been solved yet. Run model.run() first.")

        for component in self.components:
            component.set_results()

    def get_results(self, result_type: str, result_name: str, component_classes=None):
        """
        Retrieve and concatenate results from model components.

        This method collects the specified result type and name from all components
        (or a filtered subset of components), adds area and component name information
        if applicable, and concatenates the results into a single DataFrame.

        Args:
            result_type (str): Type of result to collect ('planning' or 'operation')
            result_name (str): Name of the specific result (e.g., 'power', 'power_capacity')
            component_classes (list, optional): List of Component subclasses to filter by.
                If None, results are collected from all components.

        Returns:
            pl.DataFrame: Concatenated results from all matching components

        Raises:
            ValueError: If the model has not been solved or if invalid parameters are provided
        """
        if self.linopy_model is None or not hasattr(self.linopy_model, 'solution'):
            raise ValueError("Model has not been solved yet. Run model.run() first.")

        if result_type not in ['planning', 'operation']:
            raise ValueError("Result type must be either 'planning' or 'operation'")

        # Filter components by class if specified
        if component_classes is not None:
            components = []
            for cls in component_classes:
                class_name = cls.__name__
                if class_name in self.components_by_cls:
                    components.extend(self.components_by_cls[class_name])
        else:
            components = self.components

        # Collect results from components
        result_dfs = []

        for component in components:
            # Skip components without results
            if not hasattr(component, 'results') or not component.results:
                continue

            # Skip components without the requested result type
            if result_type not in component.results:
                continue

            # Skip components without the requested result name
            if result_name not in component.results[result_type]:
                continue

            # Get the result dataframe
            result_df = component.results[result_type][result_name]

            # Skip if no data is available
            if result_df is None or result_df.is_empty():
                continue

            # Add area information if the component is area-indexed
            if component.area_indexed:
                if 'area' not in result_df.columns:
                    result_df = result_df.with_columns(pl.lit(component.area.name).alias('area'))

            # Add link information if the component is link-indexed
            if component.link_indexed:
                if 'link' not in result_df.columns:
                    result_df = result_df.with_columns(pl.lit(component.link.name).alias('link'))

            # Add resource information if the component is resource-indexed
            if component.resource_indexed:
                if 'resource' not in result_df.columns:
                    result_df = result_df.with_columns(pl.lit(component.resource).alias('resource'))

            # Add component name if the component has own_index
            if component.own_index:
                if component.own_index not in result_df.columns:
                    result_df = result_df.with_columns(pl.lit(component.name).alias("name"))

            result_dfs.append(result_df)

        # Concatenate all dataframes if any results were found
        if result_dfs:
            return pl.concat(result_dfs, how='diagonal')
        else:
            logger.warning(f"No results found for type '{result_type}' and name '{result_name}'")
            return pl.DataFrame()
