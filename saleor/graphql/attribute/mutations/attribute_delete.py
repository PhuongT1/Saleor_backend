import graphene

from ....attribute import models as models
from ....permission.enums import ProductTypePermissions
from ....webhook.event_types import WebhookEventAsyncType
from ...core import ResolveInfo
from ...core.descriptions import ADDED_IN_310
from ...core.mutations import ModelDeleteMutation, ModelWithExtRefMutation
from ...core.types import AttributeError
<<<<<<< HEAD
=======
from ...core.utils import WebhookEventInfo
>>>>>>> main
from ...plugins.dataloaders import get_plugin_manager_promise
from ..types import Attribute


class AttributeDelete(ModelDeleteMutation, ModelWithExtRefMutation):
    class Arguments:
        id = graphene.ID(required=False, description="ID of an attribute to delete.")
        external_reference = graphene.String(
            required=False,
            description=f"External ID of an attribute to delete. {ADDED_IN_310}",
        )

    class Meta:
        model = models.Attribute
        object_type = Attribute
        description = "Deletes an attribute."
        permissions = (ProductTypePermissions.MANAGE_PRODUCT_TYPES_AND_ATTRIBUTES,)
        error_type_class = AttributeError
        error_type_field = "attribute_errors"
        webhook_events_info = [
            WebhookEventInfo(
                type=WebhookEventAsyncType.ATTRIBUTE_DELETED,
                description="An attribute was deleted.",
            ),
        ]

    @classmethod
<<<<<<< HEAD
    def post_save_action(cls, info, instance, cleaned_input):
=======
    def post_save_action(cls, info: ResolveInfo, instance, cleaned_input):
>>>>>>> main
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.attribute_deleted, instance)
