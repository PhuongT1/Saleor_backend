from django.contrib.postgres.fields import jsonb
from django.contrib.postgres.fields.jsonb import KeyTransform
from django.db.models import Transform


class FilterableJSONBField(jsonb.JSONField):
    """This only redefine the JSONB field of django to register a custom lookup key
    that allow us to filter JSONB field by key value no matter what. Where django's
    behavior is to filter by key index position if the lookup value is a string number.

    This is a temporary fix waiting for a fix from django.

    Refer to https://code.djangoproject.com/ticket/30566."""

    _FROM_KEY_LOOKUP = "from_key_"
    _FROM_KEY_LOOKUP_LEN = len(_FROM_KEY_LOOKUP)

    def get_transform(self, lookup_name):
        if not lookup_name.startswith(self._FROM_KEY_LOOKUP):
            return super().get_lookup(lookup_name)
        lookup_name = lookup_name[self._FROM_KEY_LOOKUP_LEN :]  # noqa: black conflict
        return KeyTransformFactory(lookup_name)


class FromKeyLookup(Transform):
    operator = "->"
    nested_operator = "#>"

    def __init__(self, key_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_name = key_name

    def as_sql(self, compiler, connection):
        key_transforms = [self.key_name]
        previous = self.lhs

        while isinstance(previous, KeyTransform):
            key_transforms.insert(0, previous.key_name)
            previous = previous.lhs

        lhs, params = compiler.compile(previous)

        if len(key_transforms) > 1:
            return (
                "(%s %s %%s)" % (lhs, self.nested_operator),
                [key_transforms] + params,
            )

        lookup = "'%s'" % self.key_name
        return "(%s %s %s)" % (lhs, self.operator, lookup), params


class KeyTransformFactory:
    def __init__(self, key_name):
        self.key_name = key_name

    def __call__(self, *args, **kwargs):
        return FromKeyLookup(self.key_name, *args, **kwargs)
