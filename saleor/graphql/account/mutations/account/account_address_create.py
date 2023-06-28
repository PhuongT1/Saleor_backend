from typing import cast

import graphene

from .....account import models, search, utils
from .....account.error_codes import AccountErrorCode
from .....account.utils import (
    remove_the_oldest_user_address_if_address_limit_is_reached,
)
from .....core.tracing import traced_atomic_transaction
from .....permission.auth_filters import AuthorizationFilters
from .....webhook.event_types import WebhookEventAsyncType
from ....core import ResolveInfo
from ....core.doc_category import DOC_CATEGORY_USERS
from ....core.mutations import ModelMutation
from ....core.types import AccountError
from ....core.utils import WebhookEventInfo
from ....plugins.dataloaders import get_plugin_manager_promise
from ...enums import AddressTypeEnum
from ...i18n import I18nMixin
from ...types import Address, AddressInput, User


class AccountAddressCreate(ModelMutation, I18nMixin):
    user = graphene.Field(
        User, description="A user instance for which the address was created."
    )

    class Arguments:
        input = AddressInput(
            description="Fields required to create address.", required=True
        )
        type = AddressTypeEnum(
            required=False,
            description=(
                "A type of address. If provided, the new address will be "
                "automatically assigned as the customer's default address "
                "of that type."
            ),
        )

    class Meta:
        description = "Create a new address for the customer."
        doc_category = DOC_CATEGORY_USERS
        model = models.Address
        object_type = Address
        error_type_class = AccountError
        error_type_field = "account_errors"
        permissions = (AuthorizationFilters.AUTHENTICATED_USER,)
        webhook_events_info = [
            WebhookEventInfo(
                type=WebhookEventAsyncType.CUSTOMER_UPDATED,
                description="A customer account was updated.",
            ),
            WebhookEventInfo(
                type=WebhookEventAsyncType.ADDRESS_CREATED,
                description="An address was created.",
            ),
        ]

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, input, type=None
    ):
        address_type = type
        user = info.context.user
        user = cast(models.User, user)
        cleaned_input = cls.clean_input(info=info, instance=Address(), data=input)
        with traced_atomic_transaction():
            address = cls.validate_address(cleaned_input, address_type=address_type)
            # Check for invalid fields and return errors if necessary
            invalid_fields = cls.get_invalid_fields(cleaned_input)
            if invalid_fields:
                return cls.handle_invalid_fields(invalid_fields)
            cls.clean_instance(info, address)
            cls.save(info, address, cleaned_input)
            cls._save_m2m(info, address, cleaned_input)
            if address_type:
                manager = get_plugin_manager_promise(info.context).get()
                utils.change_user_default_address(user, address, address_type, manager)
        return AccountAddressCreate(user=user, address=address)

    @classmethod
    def get_invalid_fields(cls, cleaned_input):
        invalid_fields = []
        for field, value in cleaned_input.items():
            if not value and field not in (
                "is_default_shipping_address",
                "is_default_billing_address",
            ):
                invalid_fields.append(field)
        return invalid_fields

    @classmethod
    def handle_invalid_fields(cls, invalid_fields):
        errors = []
        for field in invalid_fields:
            error = AccountError(
                field=field,
                code=AccountErrorCode.INVALID.value,
                message=f"Invalid value for field '{field}'.",
            )
            errors.append(error)
        raise ValueError(errors)

    @classmethod
    def save(cls, info: ResolveInfo, instance, cleaned_input):
        super().save(info, instance, cleaned_input)
        user = info.context.user
        user = cast(models.User, user)
        remove_the_oldest_user_address_if_address_limit_is_reached(user)
        instance.user_addresses.add(user)
        user.search_document = search.prepare_user_search_document_value(user)
        user.save(update_fields=["search_document", "updated_at"])
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.customer_updated, user)
        cls.call_event(manager.address_created, instance)
