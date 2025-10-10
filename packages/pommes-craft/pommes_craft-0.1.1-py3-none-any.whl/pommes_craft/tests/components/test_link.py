import pytest
from pommes_craft import Link
from pommes_craft.components.area import Area
from pommes_craft import TransportTechnology



def test_link_initialization(energy_model):
    """
    Test that Link class initializes correctly with the given parameters.
    """

    with energy_model.context():
        area1 = Area("area1")
        area2 = Area("area2")

        transport_technology = TransportTechnology("electricity_line", resource="electricity")
        link = Link(
            name="test_link",
            area_from=area1,
            area_to=area2,
        )
        link.add_transport_technology(transport_technology)

    assert link.name == "test_link"
    assert link.area_from == area1
    assert link.area_to == area2
    assert transport_technology.name in link.technologies
