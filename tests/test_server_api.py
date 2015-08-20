# -*- coding: utf-8 -*-
from server.api import parse_products


class TestSearchAPI(object):
    def test_returns_20_products(self, get):
        response = get('search')
        assert response.status_code == 200
        assert 'products' in response.json
        assert len(response.json['products']) == 20

    def test_product_signature(self, get):
        response = get('search')
        product = response.json['products'][0]
        assert 'popularity' in product.keys()
        assert 'shop' in product.keys()
        shop = product['shop']
        assert 'lat' in shop
        assert 'lng' in shop

    def test_products_csv_parsing(self):
        products = parse_products()
        assert len(products) == 75523
        assert isinstance(products[0], tuple)
