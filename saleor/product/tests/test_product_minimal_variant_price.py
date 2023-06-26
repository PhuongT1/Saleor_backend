from decimal import Decimal
from unittest.mock import patch

import graphene
import pytest
from django.core.management import call_command
from prices import Money

from ...discount import RewardValueType
from ...discount.models import Promotion, Sale, SaleChannelListing
from ...product.models import Product, VariantChannelListingPromotionRule
from ..tasks import (
    update_products_discounted_prices_of_catalogues,
    update_products_discounted_prices_task,
)
from ..utils.variant_prices import (
    update_discounted_prices_for_promotion,
    update_products_discounted_price,
)


def test_update_product_discounted_price(product, channel_USD):
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_channel_listing.price = Money("4.99", "USD")
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    assert product_channel_listing.discounted_price == Money("10", "USD")

    update_products_discounted_price([product])

    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert variant_channel_listing.discounted_price == variant_channel_listing.price


def test_update_product_discounted_price_discount_on_variant(product, channel_USD):
    # given
    variant = product.variants.first()
    sale = Sale.objects.create(name="Test sale")
    discount_value = 5
    SaleChannelListing.objects.create(
        sale=sale,
        channel=channel_USD,
        discount_value=discount_value,
        currency=channel_USD.currency_code,
    )
    sale.variants.add(variant)

    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_channel_listing.price = Money("9.99", "USD")
    variant_channel_listing.discounted_price = Money("9.99", "USD")
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    assert product_channel_listing.discounted_price == Money("10", "USD")

    # when
    update_products_discounted_price([product])

    # then
    expected_price_amount = variant_channel_listing.price.amount - discount_value
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.discounted_price_amount == expected_price_amount


def test_update_product_discounted_price_without_price(
    product, channel_USD, channel_PLN
):
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    second_product_channel_listing = product.channel_listings.create(
        channel=channel_PLN
    )

    assert product_channel_listing.discounted_price == Money("10", "USD")

    update_products_discounted_price([product])

    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert second_product_channel_listing.discounted_price is None


def test_update_discounted_price_for_promotion_no_discount(product, channel_USD):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing.refresh_from_db()

    assert product_channel_listing.discounted_price == Money("10", "USD")

    # when
    update_discounted_prices_for_promotion(Product.objects.filter(id__in=[product.id]))

    # then
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert variant_channel_listing.discounted_price == variant_channel_listing.price
    assert not variant_channel_listing.promotion_rules.all()


def test_update_discounted_price_for_promotion_discount_on_variant(
    product, channel_USD
):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_price = Money("9.99", "USD")
    variant_channel_listing.price = variant_price
    variant_channel_listing.discounted_price = variant_price
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    reward_value = Decimal("2")
    promotion = Promotion.objects.create(
        name="Promotion",
    )
    rule = promotion.rules.create(
        name="Percentage promotion rule",
        promotion=promotion,
        catalogue_predicate={
            "variantPredicate": {
                "ids": [graphene.Node.to_global_id("ProductVariant", variant.id)]
            }
        },
        reward_value_type=RewardValueType.FIXED,
        reward_value=reward_value,
    )
    rule.channels.add(variant_channel_listing.channel)

    # when
    update_discounted_prices_for_promotion(Product.objects.filter(id__in=[product.id]))

    # then
    expected_price_amount = variant_price.amount - reward_value
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.promotion_rules.first() == rule
    assert variant_channel_listing.promotion_rules.first()
    assert (
        variant_channel_listing.variantlistingpromotionrule.first().discount_amount
        == reward_value
    )


def test_update_discounted_price_for_promotion_discount_on_product(
    product, channel_USD
):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_price = Money("9.99", "USD")
    variant_channel_listing.price = variant_price
    variant_channel_listing.discounted_price = variant_price
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    reward_value = Decimal("10")
    promotion = Promotion.objects.create(
        name="Promotion",
    )
    rule = promotion.rules.create(
        name="Percentage promotion rule",
        promotion=promotion,
        catalogue_predicate={
            "productPredicate": {
                "ids": [graphene.Node.to_global_id("Product", product.id)]
            }
        },
        reward_value_type=RewardValueType.PERCENTAGE,
        reward_value=reward_value,
    )
    rule.channels.add(variant_channel_listing.channel)

    # when
    update_discounted_prices_for_promotion(Product.objects.filter(id__in=[product.id]))

    # then
    expected_price_amount = round(
        variant_price.amount - variant_price.amount * reward_value / 100, 2
    )
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.promotion_rules.first() == rule
    assert (
        variant_channel_listing.variantlistingpromotionrule.first().discount_amount
        == variant_price.amount - expected_price_amount
    )


def test_update_discounted_price_for_promotion_promotion_not_applicable_for_channel(
    product, channel_USD, channel_PLN
):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_price = Money("9.99", "USD")
    variant_channel_listing.price = variant_price
    variant_channel_listing.discounted_price = variant_price
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    reward_value = Decimal("2")
    promotion = Promotion.objects.create(
        name="Promotion",
    )
    rule = promotion.rules.create(
        name="Percentage promotion rule",
        promotion=promotion,
        catalogue_predicate={
            "variantPredicate": {
                "ids": [graphene.Node.to_global_id("ProductVariant", variant.id)]
            }
        },
        reward_value_type=RewardValueType.FIXED,
        reward_value=reward_value,
    )
    rule.channels.add(channel_PLN)

    # when
    update_discounted_prices_for_promotion(Product.objects.filter(id__in=[product.id]))

    # then
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_price
    assert variant_channel_listing.discounted_price == variant_price
    assert not variant_channel_listing.promotion_rules.all()


def test_update_discounted_price_for_promotion_discount_updated(product, channel_USD):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)

    variant_price = Money("9.99", "USD")
    variant_channel_listing.price = variant_price
    variant_channel_listing.discounted_price = variant_price
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    reward_value = Decimal("2")
    promotion = Promotion.objects.create(
        name="Promotion",
    )
    rule = promotion.rules.create(
        name="Percentage promotion rule",
        promotion=promotion,
        catalogue_predicate={
            "variantPredicate": {
                "ids": [graphene.Node.to_global_id("ProductVariant", variant.id)]
            }
        },
        reward_value_type=RewardValueType.FIXED,
        reward_value=reward_value,
    )
    rule.channels.add(variant_channel_listing.channel)

    listing_promotion_rule = VariantChannelListingPromotionRule.objects.create(
        variant_channel_listing=variant_channel_listing,
        promotion_rule=rule,
        discount_amount=Decimal("1"),
        currency=channel_USD.currency_code,
    )

    # when
    update_discounted_prices_for_promotion(Product.objects.filter(id__in=[product.id]))

    # then
    expected_price_amount = variant_price.amount - reward_value
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.discounted_price_amount == expected_price_amount
    assert variant_channel_listing.promotion_rules.count() == 1
    listing_promotion_rule.refresh_from_db()
    assert listing_promotion_rule.discount_amount == reward_value


def test_update_discounted_price_for_promotion_discount_not_valid_anymore(
    product, channel_USD
):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)

    variant_price = Money("9.99", "USD")
    discounted_price = Money("5.00", "USD")
    variant_channel_listing.price = variant_price
    variant_channel_listing.discounted_price = discounted_price
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    reward_value = Decimal("2")
    promotion = Promotion.objects.create(
        name="Promotion",
    )
    rule = promotion.rules.create(
        name="Percentage promotion rule",
        promotion=promotion,
        catalogue_predicate={},
        reward_value_type=RewardValueType.FIXED,
        reward_value=reward_value,
    )
    rule.channels.add(variant_channel_listing.channel)

    listing_promotion_rule = VariantChannelListingPromotionRule.objects.create(
        variant_channel_listing=variant_channel_listing,
        promotion_rule=rule,
        discount_amount=Decimal("1"),
        currency=channel_USD.currency_code,
    )

    # when
    update_discounted_prices_for_promotion(Product.objects.filter(id__in=[product.id]))

    # then
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price_amount == variant_price.amount
    assert variant_channel_listing.discounted_price_amount == variant_price.amount
    assert variant_channel_listing.promotion_rules.count() == 0

    with pytest.raises(listing_promotion_rule._meta.model.DoesNotExist):
        listing_promotion_rule.refresh_from_db()


def test_update_products_discounted_prices_of_catalogues_for_product(
    product, channel_USD
):
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(channel_id=channel_USD.id)
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_channel_listing.price = Money("0.99", "USD")
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()

    assert product_channel_listing.discounted_price == Money("10", "USD")

    update_products_discounted_prices_of_catalogues(product_ids=[product.pk])

    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert variant_channel_listing.discounted_price == variant_channel_listing.price


@patch("saleor.product.utils.variant_prices.update_products_discounted_prices")
def test_update_products_discounted_prices_of_catalogues_via_products(
    mock_update_products_discounted_prices, product, product_list
):
    # given

    # when
    update_products_discounted_prices_of_catalogues(
        product_ids=[product.pk, product_list[0].pk]
    )

    # then
    mock_update_products_discounted_prices.assert_called_once()
    args, _kwargs = mock_update_products_discounted_prices.call_args
    assert set(args[0].values_list("pk", flat=True)) == {product.pk, product_list[0].pk}


@patch("saleor.product.utils.variant_prices.update_products_discounted_prices")
def test_update_products_discounted_prices_of_catalogues_via_category(
    mock_update_products_discounted_prices,
    product,
    product_list,
    category_with_image,
    category,
):
    # given
    assert category.pk != category_with_image.pk
    product.category = category_with_image
    product.save()

    # when
    update_products_discounted_prices_of_catalogues(category_ids=[category.pk])

    # then
    mock_update_products_discounted_prices.assert_called_once()
    args, _kwargs = mock_update_products_discounted_prices.call_args
    assert set(args[0].values_list("pk", flat=True)) == {p.pk for p in product_list}


@patch("saleor.product.utils.variant_prices.update_products_discounted_prices")
def test_update_products_discounted_prices_of_catalogues_via_collection(
    mock_update_products_discounted_prices, product, product_list, collection
):
    # given
    collection.products.add(*product_list)

    # when
    update_products_discounted_prices_of_catalogues(collection_ids=[collection.pk])

    # then
    mock_update_products_discounted_prices.assert_called_once()
    args, _kwargs = mock_update_products_discounted_prices.call_args
    assert set(args[0].values_list("pk", flat=True)) == {p.pk for p in product_list}


@patch("saleor.product.utils.variant_prices.update_products_discounted_prices")
def test_update_products_discounted_prices_of_catalogues_via_variants(
    mock_update_products_discounted_prices, product, product_list
):
    # given
    variant_ids = [p.variants.first().pk for p in product_list]

    # when
    update_products_discounted_prices_of_catalogues(variant_ids=variant_ids)

    # then
    mock_update_products_discounted_prices.assert_called_once()
    args, _kwargs = mock_update_products_discounted_prices.call_args
    assert set(args[0].values_list("pk", flat=True)) == {p.pk for p in product_list}


def test_update_products_discounted_prices_of_catalogues_for_category(
    category, product, channel_USD
):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(
        channel=channel_USD,
        variant=variant,
    )
    variant_channel_listing.price = Money("0.89", "USD")
    variant_channel_listing.save()
    product_channel_listing = product.channel_listings.get(
        channel_id=channel_USD.id, product_id=product.id
    )
    product_channel_listing.refresh_from_db()

    assert product_channel_listing.discounted_price == Money("10", "USD")

    # when
    update_products_discounted_prices_of_catalogues(category_ids=[product.category_id])

    # then
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert variant_channel_listing.discounted_price == variant_channel_listing.price


def test_update_products_discounted_prices_of_catalogues_for_collection(
    collection, product, channel_USD
):
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(
        channel=channel_USD,
        variant=variant,
    )
    variant_channel_listing.price = Money("0.79", "USD")
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()
    collection.products.add(product)
    assert product_channel_listing.discounted_price == Money("10", "USD")

    update_products_discounted_prices_of_catalogues(collection_ids=[collection.pk])
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert variant_channel_listing.discounted_price == variant_channel_listing.price


def test_update_products_discounted_prices_of_catalogues_for_variants(
    collection, product, channel_USD
):
    # given
    variant = product.variants.first()
    variant_channel_listing = variant.channel_listings.get(
        channel=channel_USD,
        variant=variant,
    )
    variant_channel_listing.price = Money("0.79", "USD")
    product_channel_listing = product.channel_listings.get(channel_id=channel_USD.id)
    variant_channel_listing.save()
    product_channel_listing.refresh_from_db()
    collection.products.add(product)
    assert product_channel_listing.discounted_price == Money("10", "USD")

    # when
    update_products_discounted_prices_of_catalogues(variant_ids=[variant.pk])

    # then
    product_channel_listing.refresh_from_db()
    variant_channel_listing.refresh_from_db()
    assert product_channel_listing.discounted_price == variant_channel_listing.price
    assert variant_channel_listing.discounted_price == variant_channel_listing.price


def test_update_products_discounted_prices_task(product_list):
    price = Money("0.01", "USD")
    for product in product_list:
        product_channel_listing = product.channel_listings.get()
        assert product_channel_listing.discounted_price != price
        variant = product.variants.first()
        variant_channel_listing = variant.channel_listings.get()
        variant_channel_listing.price = price
        variant_channel_listing.save()
        # Check that "variant.save()" doesn't update the "discounted_price"
        assert product_channel_listing.discounted_price != price
    update_products_discounted_prices_task.apply(
        kwargs={"product_ids": [product.pk for product in product_list]}
    )
    for product in product_list:
        product.refresh_from_db()
        product_channel_listing = product.channel_listings.get()
        assert product_channel_listing.discounted_price == price


@patch(
    "saleor.product.management.commands"
    ".update_all_products_discounted_prices"
    ".update_products_discounted_price"
)
def test_management_commmand_update_all_products_discounted_price(
    mock_update_product_discounted_price, product_list
):
    call_command("update_all_products_discounted_prices")
    call_args_list = mock_update_product_discounted_price.call_args_list
    for (args, kwargs), product in zip(call_args_list, product_list):
        assert args[0] == [product]
