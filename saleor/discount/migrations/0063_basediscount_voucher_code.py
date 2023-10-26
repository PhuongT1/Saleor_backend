from django.db import migrations
from django.db.models import Exists, OuterRef

# For batch size 1000 with 10_000 per model OrderDiscount/Voucher/VoucherCode objects
# OrderDiscount Migration took 2.39 seconds.
# OrderDiscount Memory usage increased by 15.65 MiB.
# OrderLineDiscount Migration took 2.48 seconds.
# OrderLineDiscount Memory usage increased by 4.61 MiB.
# CheckoutLineDiscount Migration took 2.26 seconds.
# CheckoutLineDiscount Memory usage increased by 3.23 MiB.

# For batch size 1000 with 100_000 per model OrderDiscount/Voucher/VoucherCode objects
# OrderDiscount Migration took 28.68 seconds.
# OrderDiscount Memory usage increased by 163.00 MiB.
# OrderLineDiscount Migration took 27.98 seconds.
# OrderLineDiscount Memory usage increased by 47.99 MiB.
# CheckoutLineDiscount Migration took 28.12 seconds.
# CheckoutLineDiscount Memory usage increased by 35.52 MiB.
BATCH_SIZE = 1000


def queryset_in_batches(queryset):
    start_pk = 0

    while True:
        qs = queryset.order_by("pk").filter(pk__gt=start_pk)[:BATCH_SIZE]
        pks = list(qs.values_list("pk", flat=True))

        if not pks:
            break

        yield pks

        start_pk = pks[-1]


def set_voucher_code_in_model(ModelName, apps, schema_editor):
    ModelDiscount = apps.get_model("discount", ModelName)
    Voucher = apps.get_model("discount", "Voucher")
    VoucherCode = apps.get_model("discount", "VoucherCode")
    set_voucher_to_voucher_code(ModelDiscount, Voucher, VoucherCode)


def set_voucher_to_voucher_code(ModelDiscount, Voucher, VoucherCode) -> None:
    model_discounts = ModelDiscount.objects.filter(
        voucher__isnull=False, voucher_code__isnull=True
    ).order_by("pk")
    for ids in queryset_in_batches(model_discounts):
        qs = ModelDiscount.objects.filter(pk__in=ids)
        set_voucher_code(ModelDiscount, Voucher, VoucherCode, qs)


def set_voucher_code(ModelDiscount, Voucher, VoucherCode, model_discounts) -> None:
    voucher_id_to_code_map = get_discount_voucher_id_to_code_map(
        Voucher, model_discounts
    )
    model_discounts_list = []
    for model_discount in model_discounts:
        code = voucher_id_to_code_map[model_discount.voucher_id]
        model_discount.voucher_code = code
        model_discounts_list.append(model_discount)
    ModelDiscount.objects.bulk_update(model_discounts_list, ["voucher_code"])


def get_discount_voucher_id_to_code_map(Voucher, model_discounts):
    vouchers = Voucher.objects.filter(
        Exists(model_discounts.filter(voucher_id=OuterRef("pk")))
    )
    voucher_id_to_code_map = {
        voucher_id: code for voucher_id, code in vouchers.values_list("id", "code")
    }
    return voucher_id_to_code_map


class Migration(migrations.Migration):
    dependencies = [
        ("discount", "0062_basediscount_voucher_code_add_index"),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: set_voucher_code_in_model(
                "OrderDiscount", apps, schema_editor
            ),
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            lambda apps, schema_editor: set_voucher_code_in_model(
                "OrderLineDiscount", apps, schema_editor
            ),
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            lambda apps, schema_editor: set_voucher_code_in_model(
                "CheckoutLineDiscount", apps, schema_editor
            ),
            migrations.RunPython.noop,
        ),
    ]
