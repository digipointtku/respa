import pytest
from guardian.shortcuts import assign_perm
from rest_framework.reverse import reverse

from ..factories import ProductFactory
from ..models import Order, ProductCustomerGroup

from resources.models.utils import generate_id

CHECK_PRICE_URL = reverse('order-check-price')


PRICE_ENDPOINT_ORDER_FIELDS = {
    'order_lines', 'price', 'begin', 'end'
}

ORDER_LINE_FIELDS = {
    'product', 'quantity', 'price', 'unit_price'
}

PRODUCT_FIELDS = {
    'id', 'type', 'name', 'description', 'price', 'max_quantity',
    'product_customer_groups'
}

PRICE_FIELDS = {'type'}


def get_detail_url(order):
    return reverse('order-detail', kwargs={'order_number': order.order_number})


@pytest.fixture(autouse=True)
def auto_use_django_db(db):
    pass


@pytest.fixture
def product(resource_in_unit):
    return ProductFactory(resources=[resource_in_unit])


@pytest.fixture
def product_2(resource_in_unit):
    return ProductFactory(resources=[resource_in_unit])


def test_order_price_check_success(user_api_client, product, two_hour_reservation):
    """Test the endpoint returns price calculations for given product without persisting anything"""

    order_count_before = Order.objects.count()

    price_check_data = {
        "order_lines": [
            {
                "product": product.product_id,
            }
        ],
        "begin": str(two_hour_reservation.begin),
        "end": str(two_hour_reservation.end)
    }

    response = user_api_client.post(CHECK_PRICE_URL, price_check_data)
    assert response.status_code == 200
    assert len(response.data['order_lines']) == 1
    assert set(response.data.keys()) == PRICE_ENDPOINT_ORDER_FIELDS
    for ol in response.data['order_lines']:
        assert set(ol.keys()) == ORDER_LINE_FIELDS
        assert set(ol['product']) == PRODUCT_FIELDS
        assert all(f in ol['product']['price'] for f in PRICE_FIELDS)

    # Check order count didn't change
    assert order_count_before == Order.objects.count()


def test_order_price_check_begin_time_after_end_time(user_api_client, product, two_hour_reservation):
    """Test the endpoint returns 400 for bad time input"""

    order_count_before = Order.objects.count()

    price_check_data = {
        "order_lines": [
            {
                "product": product.product_id,
            }
        ],
        # Begin and end input swapped to cause ValidationError
        "begin": str(two_hour_reservation.end),
        "end": str(two_hour_reservation.begin),
    }

    response = user_api_client.post(CHECK_PRICE_URL, price_check_data)
    assert response.status_code == 400


@pytest.mark.django_db
def test_order_price_check_success_customer_group(user_api_client, product_with_product_cg, two_hour_reservation):
    prod_cg = ProductCustomerGroup.objects.get(product=product_with_product_cg)
    order_count_before = Order.objects.count()
    price_check_data = {
        "order_lines": [
            {
                "product": product_with_product_cg.product_id,
            }
        ],
        "begin": str(two_hour_reservation.begin),
        "end": str(two_hour_reservation.end),
        "customer_group": prod_cg.customer_group.id
    }
    response = user_api_client.post(CHECK_PRICE_URL, price_check_data)
    
    assert response.status_code == 200
    assert len(response.data['order_lines']) == 1

    order_line = dict((key, val) for key, val in enumerate(response.data['order_lines'])).get(0, None)

    assert order_line is not None
    assert order_line['price'] == str(prod_cg.price * 2) # Two hour price
    assert order_count_before == Order.objects.count()

def test_order_price_check_invalid_customer_group(user_api_client, product, two_hour_reservation):
    """Test the endpoint returns 400 for non-existant customer_group"""

    order_count_before = Order.objects.count()

    price_check_data = {
        "order_lines": [
            {
                "product": product.product_id,
            }
        ],
        "begin": str(two_hour_reservation.begin),
        "end": str(two_hour_reservation.end),
        "customer_group": generate_id()
    }

    response = user_api_client.post(CHECK_PRICE_URL, price_check_data)
    assert response.status_code == 400