from django.core.exceptions import ValidationError


class UserDeleteMixin:
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance, errors):
        user = info.context.user
        if instance == user:
            raise ValidationError({
                'id': 'You cannot delete your own account.'})
        elif instance.is_superuser:
            raise ValidationError({'id': 'Cannot delete this account.'})


class CustomerDeleteMixin(UserDeleteMixin):
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance, errors):
        super().clean_instance(info, instance, errors)
        if instance.is_staff:
            raise ValidationError({'id': 'Cannot delete a staff account.'})


class StaffDeleteMixin(UserDeleteMixin):
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance, errors):
        super().clean_instance(info, instance, errors)
        if not instance.is_staff:
            raise ValidationError({'id': 'Cannot delete a non-staff user.'})
