from pathlib import Path
import importlib
import inspect

data_path = Path(__file__).parent / "data"
studies_path = data_path / "studies"
test_data_path = data_path / "tests"

test_data_path.mkdir(exist_ok=True)
studies_path.mkdir(exist_ok=True)

# Import EnergyModel
from pommes_craft.core.model import EnergyModel

# Import all the classes defined in components subpackage
# Get the directory of the components subpackage
components_dir = Path(__file__).parent / "components"

# Initialize an empty list to store all classes
__all__ = []

# Check if the components directory exists
if components_dir.exists() and components_dir.is_dir():
    # Iterate through all Python files in the components directory
    for file_path in components_dir.glob("*.py"):
        # Skip the components/__init__.py file itself
        if file_path.name == "__init__.py":
            continue

        # Get the module name (file name without .py extension)
        module_name = file_path.stem

        # Import the module from the components subpackage
        module = importlib.import_module(f".components.{module_name}", package=__name__)

        # Find all classes defined in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Only add classes that were defined in this module (not imported from elsewhere)
            if obj.__module__ == f"{__name__}.components.{module_name}":
                # Add the class to the current namespace (main package level)
                globals()[name] = obj
                # Add the class name to __all__
                __all__.append(name)
