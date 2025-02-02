from datetime import timedelta
from decimal import Decimal

import pytest
from rest_framework.reverse import reverse

from ..factories import (
    ProductFactory, CustomerGroupLoginMethodFactory, ProductCustomerGroupFactory,
    CustomerGroupFactory
)
from ..models import Product
from .test_order_api import PRODUCT_FIELDS

LIST_URL = reverse('resource-list')


def get_detail_url(resource):
    return reverse('resource-detail', kwargs={'pk': resource.pk})


@pytest.fixture(autouse=True)
def auto_use_django_db(db):
    pass


@pytest.mark.parametrize('price_type', (Product.PRICE_FIXED, Product.PRICE_PER_PERIOD))
@pytest.mark.parametrize('endpoint', ('list', 'detail'))
def test_get_resource_check_products(endpoint, price_type, user_api_client, resource_in_unit):
    # When using ProductFactory to create a product, it actually creates one
    # additional archived version of the same product, because factoryboy and
    # our same table versioned Products don't play together flawlessly. But
    # we can use that "feature" to our advantage here, as we can check that
    # those extra versions aren't returned by the resource API. We have an
    # assert here to make sure the "feature" isn't fixed.
    product = ProductFactory.create(
        tax_percentage=Decimal('24.00'),
        price=Decimal('10.00'),
        price_type=price_type,
        resources=[resource_in_unit],
        price_period=timedelta(hours=1) if price_type == Product.PRICE_PER_PERIOD else None,
    )
    assert Product.objects.count() == 2

    if endpoint == 'list':
        url = LIST_URL
    else:
        url = get_detail_url(resource_in_unit)
    response = user_api_client.get(url)

    assert response.status_code == 200

    if endpoint == 'list':
        products_data = response.data['results'][0]['products']
    else:
        products_data = response.data['products']
    assert len(products_data) == 1

    product_data = products_data[0]
    assert set(product_data.keys()) == PRODUCT_FIELDS
    assert product_data['id'] == product.product_id
    assert product_data['name'] == {'fi': product.name_fi}
    assert product_data['description'] == {'fi': product.description}
    assert product_data['max_quantity'] == product.max_quantity

    price_data = product_data['price']
    price_fields = {'type', 'amount', 'tax_percentage'}
    if price_type == Product.PRICE_PER_PERIOD:
        price_fields.add('period')
    assert set(price_data.keys()) == price_fields
    assert price_data['amount'] == str(product.price)
    assert price_data['type'] == product.price_type
    assert price_data['tax_percentage'] == str(product.tax_percentage)
    if price_type == Product.PRICE_PER_PERIOD:
        assert price_data['period'] == '01:00:00'
        price_fields.add('period')
    assert set(price_data.keys()) == price_fields


def test_get_resource_products_cg_allowed_login_methods_when_included(
    user_api_client, resource_in_unit):
    '''
    Tests that product customer group "only for login methods" is shown correctly
    when cg contains such login methods
    '''
    cg_login_method_1 = CustomerGroupLoginMethodFactory.create()
    cg_login_method_2 = CustomerGroupLoginMethodFactory.create()

    cg = CustomerGroupFactory.create()
    cg.only_for_login_methods.set([cg_login_method_1, cg_login_method_2])
    cg.save()
    product = ProductFactory.create(
        resources=[resource_in_unit]
    )
    pcg = ProductCustomerGroupFactory.create(customer_group=cg)
    pcg.product = product
    pcg.save()

    url = get_detail_url(resource_in_unit)
    response = user_api_client.get(url)
    products_data = response.data['products']
    assert len(products_data) == 1
    product_data = products_data[0]
    cg_data = product_data['product_customer_groups'][0]['customer_group']
    assert len(cg_data['only_for_login_methods']) == 2
    assert cg_data['only_for_login_methods'] == [
        {'login_method_id': cg_login_method_1.login_method_id},
        {'login_method_id': cg_login_method_2.login_method_id}
    ]


def test_get_resource_products_cg_allowed_login_methods_when_not_included(
    user_api_client, resource_in_unit, product_with_product_cg):
    '''
    Tests that product customer group "only for login methods" is shown correctly
    when cg does not contain any such login methods
    '''
    url = get_detail_url(resource_in_unit)
    response = user_api_client.get(url)
    products_data = response.data['products']
    assert len(products_data) == 1
    product_data = products_data[0]
    cg_data = product_data['product_customer_groups'][0]['customer_group']
    assert cg_data['only_for_login_methods'] == []
