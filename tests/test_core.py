import io
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import pytest
from django.conf import settings
from django.shortcuts import reverse
from prices import Money

from saleor.account.models import Address, User
from saleor.core.storages import S3MediaStorage
from saleor.core.templatetags.urls import _get_internal_page_slug, \
    get_internal_page_url
from saleor.core.utils import (
    Country, create_superuser, create_thumbnails, format_money,
    get_country_by_ip, get_currency_for_country, random_data)
from saleor.core.utils.text import get_cleaner, strip_html
from saleor.discount.models import Sale, Voucher
from saleor.menu.models import Menu
from saleor.order.models import Order
from saleor.page.models import Page
from saleor.product.models import Product, ProductImage
from saleor.shipping.models import ShippingMethod

type_schema = {
    'Vegetable': {
        'category': {
            'name': 'Food',
            'image_name': 'books.jpg'},
        'product_attributes': {
            'Sweetness': ['Sweet', 'Sour'],
            'Healthiness': ['Healthy', 'Not really']},
        'variant_attributes': {
            'GMO': ['Yes', 'No']},
        'images_dir': 'candy/',
        'is_shipping_required': True}}


def test_format_money():
    money = Money('123.99', 'USD')
    assert format_money(money) == '$123.99'


@pytest.mark.parametrize('ip_data, expected_country', [
    ({'country': {'iso_code': 'PL'}}, Country('PL')),
    ({'country': {'iso_code': 'UNKNOWN'}}, None),
    (None, None),
    ({}, None),
    ({'country': {}}, None)])
def test_get_country_by_ip(ip_data, expected_country, monkeypatch):
    monkeypatch.setattr(
        'saleor.core.utils.georeader.get',
        Mock(return_value=ip_data))
    country = get_country_by_ip('127.0.0.1')
    assert country == expected_country


@pytest.mark.parametrize('country, expected_currency', [
    (Country('PL'), 'PLN'),
    (Country('US'), 'USD'),
    (Country('GB'), 'GBP')])
def test_get_currency_for_country(country, expected_currency, monkeypatch):
    currency = get_currency_for_country(country)
    assert currency == expected_currency


def test_create_superuser(db, client):
    credentials = {'email': 'admin@example.com', 'password': 'admin'}
    # Test admin creation
    assert User.objects.all().count() == 0
    create_superuser(credentials)
    assert User.objects.all().count() == 1
    admin = User.objects.all().first()
    assert admin.is_superuser
    # Test duplicating
    create_superuser(credentials)
    assert User.objects.all().count() == 1
    # Test logging in
    response = client.post(reverse('account:login'),
                           {'username': credentials['email'],
                            'password': credentials['password']},
                           follow=True)
    assert response.context['request'].user == admin


def test_create_shipping_methods(db):
    assert ShippingMethod.objects.all().count() == 0
    for _ in random_data.create_shipping_methods():
        pass
    assert ShippingMethod.objects.all().count() == 2


def test_create_fake_user(db):
    assert User.objects.all().count() == 0
    random_data.create_fake_user()
    assert User.objects.all().count() == 1
    user = User.objects.all().first()
    assert not user.is_superuser


def test_create_fake_users(db):
    how_many = 5
    for _ in random_data.create_users(how_many):
        pass
    assert User.objects.all().count() == 5


def test_create_address(db):
    assert Address.objects.all().count() == 0
    random_data.create_address()
    assert Address.objects.all().count() == 1


def test_create_attribute(db):
    data = {'slug': 'best_attribute', 'name': 'Best attribute'}
    attribute = random_data.create_attribute(**data)
    assert attribute.name == data['name']
    assert attribute.slug == data['slug']


def test_create_product_types_by_schema(db):
    product_type = random_data.create_product_types_by_schema(
        type_schema)[0][0]
    assert product_type.name == 'Vegetable'
    assert product_type.product_attributes.count() == 2
    assert product_type.variant_attributes.count() == 1
    assert product_type.is_shipping_required


@patch('saleor.core.utils.random_data.create_product_thumbnails.delay')
def test_create_products_by_type(
        mock_create_thumbnails, db, monkeypatch, product_image):
    # Tests shouldn't depend on images present in placeholder folder
    monkeypatch.setattr(
        'saleor.core.utils.random_data.get_image',
        Mock(return_value=product_image))
    dummy_file_names = ['example.jpg', 'example2.jpg']
    monkeypatch.setattr(
        'saleor.core.utils.random_data.os.listdir',
        Mock(return_value=dummy_file_names))

    assert Product.objects.all().count() == 0
    how_many = 5
    product_type = random_data.create_product_types_by_schema(
        type_schema)[0][0]
    random_data.create_products_by_type(
        product_type, type_schema['Vegetable'], '/',
        how_many=how_many, create_images=True)
    assert Product.objects.all().count() == how_many
    assert mock_create_thumbnails.called


def test_create_fake_order(db, monkeypatch, product_image):
    # Tests shouldn't depend on images present in placeholder folder
    monkeypatch.setattr(
        'saleor.core.utils.random_data.get_image',
        Mock(return_value=product_image))
    for _ in random_data.create_shipping_methods():
        pass
    for _ in random_data.create_users(3):
        pass
        random_data.create_products_by_schema('/', 10, False)
    how_many = 5
    for _ in random_data.create_orders(how_many):
        pass
    assert Order.objects.all().count() == 5


def test_create_product_sales(db):
    how_many = 5
    for _ in random_data.create_product_sales(how_many):
        pass
    assert Sale.objects.all().count() == 5


def test_create_vouchers(db):
    assert Voucher.objects.all().count() == 0
    for _ in random_data.create_vouchers():
        pass
    assert Voucher.objects.all().count() == 2


def test_manifest(client, site_settings):
    response = client.get(reverse('manifest'))
    assert response.status_code == 200
    content = response.json()
    assert content['name'] == site_settings.site.name
    assert content['short_name'] == site_settings.site.name
    assert content['description'] == site_settings.description


def test_utils_get_cleaner_invalid_parameters():
    with pytest.raises(ValueError):
        get_cleaner(bad=True)


def test_utils_strip_html():
    base_text = ('<p>Hello</p>'
                 '\n\n'
                 '\t<b>World</b>')
    text = strip_html(base_text, strip_whitespace=True)
    assert text == 'Hello World'


def test_create_thumbnails(product_with_image, settings):
    settings.VERSATILEIMAGEFIELD_SETTINGS['create_images_on_demand'] = False
    sizeset = settings.VERSATILEIMAGEFIELD_RENDITION_KEY_SETS['products']
    product_image = product_with_image.images.first()

    # There's no way to list images created by versatile prewarmer
    # So we delete all created thumbnails/crops and count them
    log_deleted_images = io.StringIO()
    with redirect_stdout(log_deleted_images):
        product_image.image.delete_all_created_images()
    log_deleted_images = log_deleted_images.getvalue()
    # Image didn't have any thumbnails/crops created, so there's no log
    assert not log_deleted_images

    create_thumbnails(product_image.pk, ProductImage, 'products')
    log_deleted_images = io.StringIO()
    with redirect_stdout(log_deleted_images):
        product_image.image.delete_all_created_images()
    log_deleted_images = log_deleted_images.getvalue()

    for image_name, method_size in sizeset:
        method, size = method_size.split('__')
        if method == 'crop':
            assert product_image.image.crop[size].name in log_deleted_images
        elif method == 'thumbnail':
            assert product_image.image.thumbnail[size].name in log_deleted_images  # noqa


@patch('storages.backends.s3boto3.S3Boto3Storage')
@patch.object(settings, 'AWS_MEDIA_BUCKET_NAME', 'media-bucket')
@patch.object(settings, 'AWS_MEDIA_CUSTOM_DOMAIN', 'media-bucket.example.org')
def test_storages_set_s3_bucket_domain(*_patches):
    assert settings.AWS_MEDIA_BUCKET_NAME == 'media-bucket'
    assert settings.AWS_MEDIA_CUSTOM_DOMAIN == 'media-bucket.example.org'
    storage = S3MediaStorage()
    assert storage.bucket_name == 'media-bucket'
    assert storage.custom_domain == 'media-bucket.example.org'


@patch('storages.backends.s3boto3.S3Boto3Storage')
@patch.object(settings, 'AWS_MEDIA_BUCKET_NAME', 'media-bucket')
def test_storages_not_setting_s3_bucket_domain(*_patches):
    assert settings.AWS_MEDIA_BUCKET_NAME == 'media-bucket'
    assert settings.AWS_MEDIA_CUSTOM_DOMAIN is None
    storage = S3MediaStorage()
    assert storage.bucket_name == 'media-bucket'
    assert storage.custom_domain is None


def test_random_data_get_default_page_content_missing_file():
    html = random_data.get_default_page_content('__missing_file__')
    assert html == random_data.DEFAULT_PAGE_HTML_IF_MISSING


def test_random_data_create_privacy_page(footer: Menu):
    slug = _get_internal_page_slug('PrivacyPolicy')

    # default pages object can be already created by default in migration
    assert Page.objects.all().delete()
    assert Page.objects.all().count() == 0
    assert footer.items.count() == 0

    assert list(random_data.create_privacy_page(create_menu_entry=True))
    assert Page.objects.all().count() == 1
    assert footer.items.count() == 1

    created_page = Page.objects.all().last()
    menu_item = footer.items.last()
    assert created_page.slug == slug
    assert created_page.content != random_data.DEFAULT_PAGE_HTML_IF_MISSING
    assert menu_item.name == created_page.title
    assert menu_item.page_id == created_page.pk

    created_page.title = title = 'New title was placed'
    created_page.content = content = 'New content was placed'
    created_page.save()

    menu_item.name = menu_item_name = 'New name'
    menu_item.save()

    # check if not overriding
    assert not list(random_data.create_privacy_page(create_menu_entry=True))
    assert Page.objects.all().count() == 1
    assert footer.items.count() == 1

    created_page = Page.objects.all().last()
    menu_item = footer.items.last()
    assert created_page.title == title
    assert created_page.content == content
    assert menu_item.name == menu_item_name

    # test without creating menu item
    footer.items.last().delete()
    assert footer.items.count() == 0

    # should have nothing to do
    assert not list(random_data.create_privacy_page(create_menu_entry=False))
    assert Page.objects.all().count() == 1
    assert footer.items.count() == 0


def test_random_data_create_selling_contract_page(footer: Menu):
    slug = _get_internal_page_slug('SellingContract')

    # default pages object can be already created by default in migration
    assert Page.objects.all().delete()
    assert Page.objects.all().count() == 0
    assert footer.items.count() == 0

    assert list(
        random_data.create_selling_contract_page(create_menu_entry=True))
    assert Page.objects.all().count() == 1
    assert footer.items.count() == 1

    created_page = Page.objects.all().last()
    menu_item = footer.items.last()
    assert created_page.slug == slug
    assert created_page.content != random_data.DEFAULT_PAGE_HTML_IF_MISSING
    assert menu_item.name == created_page.title
    assert menu_item.page_id == created_page.pk

    created_page.title = title = 'New title was placed'
    created_page.content = content = 'New content was placed'
    created_page.save()

    menu_item.name = menu_item_name = 'New name'
    menu_item.save()

    # check if not overriding
    assert not list(
        random_data.create_selling_contract_page(create_menu_entry=True))
    assert Page.objects.all().count() == 1
    assert footer.items.count() == 1

    created_page = Page.objects.all().last()
    menu_item = footer.items.last()
    assert created_page.title == title
    assert created_page.content == content
    assert menu_item.name == menu_item_name

    # test without creating menu item
    footer.items.last().delete()
    assert footer.items.count() == 0

    # should have nothing to do
    assert not list(random_data.create_selling_contract_page(
        create_menu_entry=False))
    assert Page.objects.all().count() == 1
    assert footer.items.count() == 0


@patch.object(settings, 'INTERNAL_PAGES', {'InternalPage': 'internal-page'})
def test_templatetags_urls_get_internal_page_url():
    expected_url = reverse('page:details', kwargs={'slug': 'internal-page'})
    assert get_internal_page_url('InternalPage') == expected_url

    with pytest.raises(ValueError):
        get_internal_page_url('UnknownInternalPage')
