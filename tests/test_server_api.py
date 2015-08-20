# -*- coding: utf-8 -*-
import os
from collections import namedtuple
from mock import Mock, patch

from server.api import (
    parse_products, parse_shops, parse_csv_files, parse_tags,
    filter_products, distance, validate_search_args)


Shop = namedtuple('shop', ['id', 'lat', 'lng'])
Product = namedtuple('product', ['shop_id'])


class TestSearchView(object):
    def test_search_returns_products(self, get):
        response = get('/search')
        assert response.status_code == 200
        assert 'products' in response.json


class TestProductsFiltering:
    def test_count(self, app):
        app.products = [i for i in range(50)]
        filtered = filter_products(count=35)
        assert len(filtered) == 35

    def test_distance(self, app):
        app.shops = [Shop(id=i, lat=i, lng=10) for i in range(20)]
        app.products = [Product(shop_id=i) for i in range(20)]
        filtered = filter_products(lat=10, lng=10, radius=1000)
        assert len(filtered) == 1
        assert app.products[10] in filtered

    def test_tags(self, app):
        app.shops = [Shop(id=i, lat=i, lng=10) for i in range(20)]
        app.products = [Product(shop_id=i) for i in range(20)]
        app.tags = {
            'test': [1, 2]
        }
        filtered = filter_products(tags=[], count=10)
        assert len(filtered) == 10
        filtered = filter_products(tags=['test'], count=10)
        assert len(filtered) == 2
        assert app.products[1] in filtered
        assert app.products[2] in filtered

    def test_tags_and_distance_intersection(self, app):
        app.shops = [Shop(id=i, lat=i, lng=10) for i in range(20)]
        app.products = [Product(shop_id=i) for i in range(20)]
        app.tags = {'test': [10, 1, 20]}
        filtered = filter_products(lat=10, lng=10, radius=1e+6, tags=['test'])
        assert len(filtered) == 1
        assert app.products[10] in filtered


class TestValidation:
    def test_count_validation(self):
        assert validate_search_args({'count': 35}) == {'count': 35}
        assert validate_search_args({'count': 'asdf'}) == {}
        assert validate_search_args({'count': None}) == {}

    def test_lat_validation(self):
        assert validate_search_args({'lat': 35.123}) == {'lat': 35.123}
        assert validate_search_args({'lat': 'asdf'}) == {}
        assert validate_search_args({'lat': None}) == {}

    def test_lng_validation(self):
        assert validate_search_args({'lng': 35.123}) == {'lng': 35.123}
        assert validate_search_args({'lng': 'asdf'}) == {}
        assert validate_search_args({'lng': None}) == {}

    def test_radius_validation(self):
        assert validate_search_args({'radius': 35}) == {'radius': 35}
        assert validate_search_args({'radius': 'asdf'}) == {}
        assert validate_search_args({'radius': None}) == {}

    def test_tags_validation(self):
        assert validate_search_args({'tags': 'a, b'}) == {'tags': ['a', 'b']}
        assert validate_search_args({'tags': 'a,b'}) == {'tags': ['a', 'b']}
        assert validate_search_args({'tags': 'ab'}) == {'tags': ['ab']}
        assert validate_search_args({'tags': None}) == {}


class TestCSVParsing:
    def test_products_csv_parsing(self):
        path = os.path.join(os.path.dirname(__file__), 'products_sample.csv')
        with patch('server.api.data_path', return_value=path):
            products = parse_products()
        assert len(products) == 2
        product = products[0]
        assert product.id == '9c2a6a8f2bc443c7826653ab73f69c3f'
        assert product.shop_id == '0596486b9de44dc4ae4248cfc959e8c7'
        assert product.title == 'Ruben WD 60cm'
        assert product.popularity == 0.905
        assert product.quantity == 10

    def test_shops_csv_parsing(self):
        path = os.path.join(os.path.dirname(__file__), 'shops_sample.csv')
        with patch('server.api.data_path', return_value=path):
            shops, shops_index = parse_shops()
        assert len(shops) == len(shops_index) == 2
        shop = shops[0]
        assert shop.id == '4aa53e646bf84faca9a76c020b0682de'
        assert shop.name == 'Witting-Renner'
        assert shop.lat == 59.33265972650577
        assert shop.lng == 18.06061237898499

    def test_tags_csv_parsing(self):
        tags_path = [
            os.path.join(os.path.dirname(__file__), 'taggings_sample.csv'),
            os.path.join(os.path.dirname(__file__), 'tags_sample.csv'),
        ]
        with patch('server.api.data_path', side_effect=tags_path):
            tags = parse_tags()
        assert len(tags) == 2
        assert len(tags['trousers']) == 2

    def test_parse_csv_data(self, monkeypatch):
        products_mock, tags_mock = Mock(), Mock()
        shops_mock = Mock(return_value=(None, None))
        monkeypatch.setattr('server.api.parse_products', products_mock)
        monkeypatch.setattr('server.api.parse_shops', shops_mock)
        monkeypatch.setattr('server.api.parse_tags', tags_mock)
        parse_csv_files()
        assert shops_mock.call_count == 1
        assert products_mock.call_count == 1
        assert tags_mock.call_count == 1


class TestUtils:
    def test_distance(self):
        assert int(distance(77.1539, 120.398, 77.1804, 129.55)) == 225883
