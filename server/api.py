# -*- coding: utf-8 -*-
import random
import string
import csv
from collections import namedtuple

from flask import Blueprint, current_app, jsonify
from flask.ext.cors import CORS

api = Blueprint('api', __name__)
CORS(api)


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)


@api.before_app_first_request
def parse_products():
    global products
    products = []
    with open(data_path('products.csv')) as csvfile:
        reader = csv.reader(csvfile)
        scheme = reader.next()
        Product = namedtuple('Products', scheme)
        for line in reader:
            products.append(Product(*line))
    products = tuple(products)
    return products


def get_shop_by_id(shop_id):
    return {'lat': None, 'lng': None}


def prepare_product(product):
    prepared = product._asdict()
    prepared['shop'] = get_shop_by_id(prepared.pop('shop_id'))
    return prepared


@api.route('/search', methods=['GET'])
def search():
    filtered_products = map(prepare_product, products)
    return jsonify({'products': filtered_products[:20]})
