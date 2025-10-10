from pommes_craft.core.component import Component


class Area(Component):
    """Geographical area in the energy system."""
    area_indexed = False
    link_indexed = False
    prefix = ""
    own_index = "area"

    def __init__(self, name: str):
        """Initialize an area component.

        Args:
            name: Name of the geographical area
        """
        super().__init__(name)
        self.components = {}

    def add_component(self, component: Component):
        """
        Add a component to this area.

        Args:
            component: Component object to add to this area.

        Raises:
            ValueError: If a component with the same name already exists in this area.
        """
        if component.name in self.components:
            raise ValueError(
                f"Component name '{component.name}' already exists in area '{self.name}'"
            )

        self.components[component.name] = component
