"""Costs map used by query complexity validator.

It's three levels deep dict of dicts:

- Type
- Fields
- Complexity

To set complexity cost for querying a field "likes" on type "User":

{
    "User": {
        "likes": {"complexity": 2}
    }
}

Querying above field will not increase query complexity by 1.

If field's complexity should be multiplied by value of argument (or arguments),
you can specify names of those arguments in "multipliers" list:

{
    "Query": {
        "products": {"complexity": 1, "multipliers": ["first", "last"]}
    }
}

This will result in following queries having cost of 100:

{ products(first: 100) { edges: { id } } }

{ products(last: 100) { edges: { id } } }

{ products(first: 10, last: 10) { edges: { id } } }

Notice that complexity is in last case is multiplied by all arguments.

Complexity is also multiplied recursively:

{
    "Query": {
        "products": {"complexity": 1, "multipliers": ["first", "last"]}
    },
    "Product": {
        "shippings": {"complexity": 1},
    }
}

This query will have cost of 200 (100 x 2 for each product):

{ products(first: 100) { complexity } }
"""

COST_MAP = {
    "Query": {
        "address": {"complexity": 1},
        "addressValidationRules": {"complexity": 1},
        "app": {"complexity": 1},
        "appExtension": {"complexity": 1},
        "appExtensions": {"complexity": 1, "multipliers": ["first", "last"]},
        "apps": {"complexity": 1, "multipliers": ["first", "last"]},
        "appsInstallations": {"complexity": 1},
        "attribute": {"complexity": 1},
        "attributes": {"complexity": 1, "multipliers": ["first", "last"]},
        "categories": {"complexity": 1, "multipliers": ["first", "last"]},
        "category": {"complexity": 1},
        "channel": {"complexity": 1},
        "channels": {"complexity": 1},
        "checkout": {"complexity": 1},
        "checkoutLines": {"complexity": 1, "multipliers": ["first", "last"]},
        "checkouts": {"complexity": 1, "multipliers": ["first", "last"]},
        "collection": {"complexity": 1},
        "collections": {"complexity": 1, "multipliers": ["first", "last"]},
        "customers": {"complexity": 1, "multipliers": ["first", "last"]},
        "digitalContent": {"complexity": 1},
        "digitalContents": {"complexity": 1, "multipliers": ["first", "last"]},
        "draftOrders": {"complexity": 1, "multipliers": ["first", "last"]},
        "exportFile": {"complexity": 1},
        "exportFiles": {"complexity": 1, "multipliers": ["first", "last"]},
        "giftCard": {"complexity": 1},
        "giftCardCurrencies": {"complexity": 1},
        "giftCards": {"complexity": 1, "multipliers": ["first", "last"]},
        "giftCardTags": {"complexity": 1, "multipliers": ["first", "last"]},
        "homepageEvents": {"complexity": 1, "multipliers": ["first", "last"]},
        "me": {"complexity": 1},
        "menu": {"complexity": 1},
        "menuItem": {"complexity": 1},
        "menuItems": {"complexity": 1, "multipliers": ["first", "last"]},
        "menus": {"complexity": 1, "multipliers": ["first", "last"]},
        "order": {"complexity": 1},
        "orderByToken": {"complexity": 1},
        "orders": {"complexity": 1, "multipliers": ["first", "last"]},
        "ordersTotal": {"complexity": 1},
        "page": {"complexity": 1},
        "pages": {"complexity": 1, "multipliers": ["first", "last"]},
        "pageType": {"complexity": 1},
        "pageTypes": {"complexity": 1, "multipliers": ["first", "last"]},
        "payment": {"complexity": 1},
        "payments": {"complexity": 1, "multipliers": ["first", "last"]},
        "permissionGroup": {"complexity": 1},
        "permissionGroups": {"complexity": 1, "multipliers": ["first", "last"]},
        "plugin": {"complexity": 1},
        "plugins": {"complexity": 1, "multipliers": ["first", "last"]},
        "product": {"complexity": 1},
        "products": {"complexity": 1, "multipliers": ["first", "last"]},
        "productType": {"complexity": 1},
        "productTypes": {"complexity": 1, "multipliers": ["first", "last"]},
        "productVariant": {"complexity": 1},
        "productVariants": {"complexity": 1, "multipliers": ["first", "last"]},
        "sale": {"complexity": 1},
        "sales": {"complexity": 1, "multipliers": ["first", "last"]},
        "shippingZone": {"complexity": 1},
        "shippingZones": {"complexity": 1, "multipliers": ["first", "last"]},
        "staffUsers": {"complexity": 1, "multipliers": ["first", "last"]},
        "stock": {"complexity": 1},
        "stocks": {"complexity": 1, "multipliers": ["first", "last"]},
        "taxTypes": {"complexity": 1},
        "translation": {"complexity": 1},
        "translations": {"complexity": 1, "multipliers": ["first", "last"]},
        "user": {"complexity": 1},
        "voucher": {"complexity": 1},
        "vouchers": {"complexity": 1, "multipliers": ["first", "last"]},
        "warehouse": {"complexity": 1},
        "warehouses": {"complexity": 1, "multipliers": ["first", "last"]},
        "webhook": {"complexity": 1},
    },
    "Attribute": {
        "choices": {"complexity": 1, "multipliers": ["first", "last"]},
        "productTypes": {"complexity": 1, "multipliers": ["first", "last"]},
        "productVariantTypes": {"complexity": 1, "multipliers": ["first", "last"]},
    },
    "Category": {
        "ancestors": {"complexity": 1, "multipliers": ["first", "last"]},
        "children": {"complexity": 1, "multipliers": ["first", "last"]},
        "description": {"complexity": 1},
        "parent": {"complexity": 1},
        "products": {"complexity": 1, "multipliers": ["first", "last"]},
    },
    "Collection": {
        "channelListings": {"complexity": 1},
        "products": {"complexity": 1, "multipliers": ["first", "last"]},
    },
    "OrderLine": {
        "variant": {"complexity": 1},
    },
    "Product": {
        "attributes": {"complexity": 1},
        "category": {"complexity": 1},
        "channelListings": {"complexity": 1},
        "collections": {"complexity": 1},
        "defaultVariant": {"complexity": 1},
        "description": {"complexity": 1},
        "imageById": {"complexity": 1},
        "images": {"complexity": 1},
        "media": {"complexity": 1},
        "mediaById": {"complexity": 1},
        "pricing": {"complexity": 1},
        "productType": {"complexity": 1},
        "thumbnail": {"complexity": 1},
        "variants": {"complexity": 1},
    },
    "ProductVariant": {
        "attributes": {"complexity": 1},
        "channelListings": {"complexity": 1},
        "images": {"complexity": 1},
        "media": {"complexity": 1},
        "pricing": {"complexity": 1},
        "product": {"complexity": 1},
        "revenue": {"complexity": 1},
    },
    "SelectedAttribute": {
        "attribute": {"complexity": 1},
        "values": {"complexity": 1, "multipliers": ["first", "last"]},
    },
}
