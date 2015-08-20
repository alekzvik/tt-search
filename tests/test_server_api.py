# -*- coding: utf-8 -*-
import os
from mock import Mock, patch, mock_open

from server.api import parse_products, parse_shops, parse_csv_files


class TestSearchView(object):
    def test_returns_products(self, get):
        response = get('/search')
        assert response.status_code == 200
        assert 'products' in response.json

    @patch('server.api.filter_products', return_value=[])
    def test_search_products_count(self, fp_mock, get):
        response = get('/search?count=35')
        fp_mock.assert_called_once_with(count=35)


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

    def test_parse_csv_data(self, monkeypatch):
        products_mock = Mock()
        shops_mock = Mock(return_value=(None, None))
        monkeypatch.setattr('server.api.parse_products', products_mock)
        monkeypatch.setattr('server.api.parse_shops', shops_mock)
        parse_csv_files()
        assert shops_mock.call_count == products_mock.call_count == 1
