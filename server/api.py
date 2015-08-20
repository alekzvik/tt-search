# -*- coding: utf-8 -*-
import csv
from collections import namedtuple

from flask import Blueprint, current_app, jsonify, request
from flask.ext.cors import CORS

api = Blueprint('api', __name__)
CORS(api)


products = tuple()
shops, shops_index = tuple(), {}


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)


@api.before_app_first_request
def parse_csv_files():
    global products, shops, shops_index
    products = parse_products()
    shops, shops_index = parse_shops()


def parse_products():
    products = []
    with open(data_path('products.csv')) as csvfile:
        reader = csv.reader(csvfile)
        scheme = reader.next()
        Product = namedtuple('Product', scheme)
        for line in reader:
            products.append(Product(
                line[0], line[1], line[2], float(line[3]), int(line[4])))
    products = tuple(sorted(products, key=lambda p: p.popularity, reverse=True))
    return products


def parse_shops():
    shops = []
    shops_index = {}
    with open(data_path('shops.csv')) as csvfile:
        reader = csv.reader(csvfile)
        scheme = reader.next()
        Shop = namedtuple('Shop', scheme)
        for pos, line in enumerate(reader):
            shop = Shop(line[0], line[1], float(line[2]), float(line[3]))
            shops.append(shop)
            shops_index[shop.id] = pos
    shops = tuple(shops)
    return shops, shops_index


def get_and_prepare_shop(shop_id):
    pos = shops_index[shop_id]
    shop = shops[pos]
    return shop._asdict()


def prepare_product(product):
    prepared = product._asdict()
    prepared['shop'] = get_and_prepare_shop(prepared.pop('shop_id'))
    return prepared


def filter_products(count):
    return map(prepare_product, products)[:count]


@api.route('/search', methods=['GET'])
def search():
    count = request.args.get('count', 10)
    try:
        count = int(count)
    except ValueError:
        count = 10
    filtered_products = filter_products(count=count)
    return jsonify({'products': filtered_products})
