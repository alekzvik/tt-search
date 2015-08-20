# -*- coding: utf-8 -*-
from mock import Mock

from server.api import parse_products, parse_shops, parse_csv_files


class TestSearchAPI(object):
    def test_returns_10_products(self, get):
        response = get('/search')
        assert response.status_code == 200
        assert 'products' in response.json
        assert len(response.json['products']) == 10

    def test_product_signature(self, get):
        response = get('/search')
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

    def test_shops_csv_parsing(self):
        shops, shops_index = parse_shops()
        assert len(shops) == len(shops_index) == 10000
        assert isinstance(shops[0], tuple)

    def test_csv_parsing_is_done_before_first_request(self, app):
        assert parse_csv_files in app.before_first_request_funcs

    def test_search_products_count(self, get):
        response = get('/search?count=35')
        assert len(response.json['products']) == 35

    def test_parse_csv_data(self, monkeypatch):
        products_mock = Mock(return_value=())
        shops_mock = Mock(return_value=(None, None))
        monkeypatch.setattr('server.api.parse_products', products_mock)
        monkeypatch.setattr('server.api.parse_shops', shops_mock)
        parse_csv_files()
        assert shops_mock.call_count == products_mock.call_count == 1
