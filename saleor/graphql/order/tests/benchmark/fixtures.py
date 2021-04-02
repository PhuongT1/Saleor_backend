import uuid

import pytest
from prices import Money, TaxedMoney

from .....account.models import User
from .....order.models import Order


@pytest.fixture
def users_for_benchmarks(address):
    users = [
        User(
            email=f"john.doe.{i}@exmaple.com",
            is_active=True,
            default_billing_address=address.get_copy(),
            default_shipping_address=address.get_copy(),
            first_name="John",
            last_name="Doe",
        )
        for i in range(10)
    ]
    return User.objects.bulk_create(users)


@pytest.fixture
def orders_for_benchmarks(channel_USD, address, users_for_benchmarks):
    orders = [
        Order(
            token=str(uuid.uuid4()),
            channel=channel_USD,
            billing_address=address.get_copy(),
            shipping_address=address.get_copy(),
            user=users_for_benchmarks[i],
            total=TaxedMoney(net=Money(i, "USD"), gross=Money(i, "USD")),
        )
        for i in range(10)
    ]
    return Order.objects.bulk_create(orders)
