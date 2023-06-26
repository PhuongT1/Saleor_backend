import pytest

from .....account.models import User
from .....order.models import Order
from ....tests.utils import get_graphql_content

QUERY_CUSTOMERS_WITH_SORT = """
    query ($sort_by: UserSortingInput!) {
        customers(first:5, sortBy: $sort_by) {
                edges{
                    node{
                        firstName
                    }
                }
            }
        }
"""


@pytest.mark.parametrize(
    "customer_sort, result_order",
    [
        ({"field": "FIRST_NAME", "direction": "ASC"}, ["Joe", "John", "Leslie"]),
        ({"field": "FIRST_NAME", "direction": "DESC"}, ["Leslie", "John", "Joe"]),
        ({"field": "LAST_NAME", "direction": "ASC"}, ["John", "Joe", "Leslie"]),
        ({"field": "LAST_NAME", "direction": "DESC"}, ["Leslie", "Joe", "John"]),
        ({"field": "EMAIL", "direction": "ASC"}, ["John", "Leslie", "Joe"]),
        ({"field": "EMAIL", "direction": "DESC"}, ["Joe", "Leslie", "John"]),
        ({"field": "ORDER_COUNT", "direction": "ASC"}, ["John", "Leslie", "Joe"]),
        ({"field": "ORDER_COUNT", "direction": "DESC"}, ["Joe", "Leslie", "John"]),
        ({"field": "CREATED_AT", "direction": "ASC"}, ["John", "Joe", "Leslie"]),
        ({"field": "CREATED_AT", "direction": "DESC"}, ["Leslie", "Joe", "John"]),
        ({"field": "LAST_MODIFIED_AT", "direction": "ASC"}, ["Leslie", "John", "Joe"]),
        ({"field": "LAST_MODIFIED_AT", "direction": "DESC"}, ["Joe", "John", "Leslie"]),
    ],
)
def test_query_customers_with_sort(
    customer_sort, result_order, staff_api_client, permission_manage_users, channel_USD
):
    users = User.objects.bulk_create(
        [
            User(
                first_name="John",
                last_name="Allen",
                email="allen@example.com",
                is_staff=False,
                is_active=True,
            ),
            User(
                first_name="Joe",
                last_name="Doe",
                email="zordon01@example.com",
                is_staff=False,
                is_active=True,
            ),
            User(
                first_name="Leslie",
                last_name="Wade",
                email="leslie@example.com",
                is_staff=False,
                is_active=True,
            ),
        ]
    )

    users[2].save()
    users[0].save()
    users[1].save()

    Order.objects.create(
        user=User.objects.get(email="zordon01@example.com"), channel=channel_USD
    )

    variables = {"sort_by": customer_sort}
    staff_api_client.user.user_permissions.add(permission_manage_users)
    response = staff_api_client.post_graphql(QUERY_CUSTOMERS_WITH_SORT, variables)
    content = get_graphql_content(response)
    users = content["data"]["customers"]["edges"]

    for order, user_first_name in enumerate(result_order):
        assert users[order]["node"]["firstName"] == user_first_name
