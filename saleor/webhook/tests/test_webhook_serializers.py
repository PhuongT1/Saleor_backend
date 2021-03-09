from operator import itemgetter
from unittest.mock import ANY

from ..serializers import serialize_product_attributes


def test_serialize_product_attributes(
    product_with_variant_with_two_attributes, product_with_multiple_values_attributes
):
    variant_data = serialize_product_attributes(
        product_with_variant_with_two_attributes.variants.first()
    )
    product_data = serialize_product_attributes(product_with_multiple_values_attributes)

    assert len(variant_data) == 2
    assert variant_data[1] == {
        "id": ANY,
        "name": "Size",
        "values": [{"name": "Small", "slug": "small", "value": ""}],
    }

    assert len(product_data) == 1
    assert product_data[0]["name"] == "Available Modes"
    assert sorted(product_data[0]["values"], key=itemgetter("name")) == [
        {"name": "Eco Mode", "value": "", "slug": "eco"},
        {"name": "Performance Mode", "value": "", "slug": "power"},
    ]
