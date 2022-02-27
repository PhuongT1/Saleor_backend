import graphene
from graphene import relay
from ....graphql.core.connection import CountableDjangoObjectType

from .. import models


class Vendor(CountableDjangoObjectType):
    class Meta:
        model = models.Vendor
        filter_fields = ["id", "name", "country"]
        interfaces = (graphene.relay.Node,)
        exclude = ["users"]


class VendorConnection(relay.Connection):
    class Meta:
        node = Vendor


class Billing(CountableDjangoObjectType):
    class Meta:
        model = models.BillingInfo
        filter_fields = ["id", "iban", "bank_name"]
        interfaces = (graphene.relay.Node,)


class BillingConnection(relay.Connection):
    class Meta:
        node = Billing
