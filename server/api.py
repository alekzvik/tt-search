# -*- coding: utf-8 -*-
from __future__ import division
import csv
import math
from collections import namedtuple

from flask import Blueprint, current_app, jsonify, request
from flask.ext.cors import CORS

api = Blueprint('api', __name__)
CORS(api)


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)


@api.before_app_first_request
def parse_csv_files():
    current_app.products = parse_products()
    current_app.shops, current_app.shops_index = parse_shops()
    current_app.tags = parse_tags()


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


def parse_tags():
    temp, tags = {}, {}
    with open(data_path('taggings.csv')) as csvfile:
        reader = csv.reader(csvfile)
        reader.next()
        for id, shop_id, tag_id in reader:
            temp[tag_id] = temp.get(tag_id, []) + [shop_id]
    with open(data_path('tags.csv')) as csvfile:
        reader = csv.reader(csvfile)
        reader.next()
        for id, tag in reader:
            tags[tag] = temp[id]
    return tags


def get_and_prepare_shop(shop_id):
    pos = current_app.shops_index[shop_id]
    shop = current_app.shops[pos]
    return shop._asdict()


def prepare_product(product):
    prepared = product._asdict()
    prepared['shop'] = get_and_prepare_shop(prepared.pop('shop_id'))
    return prepared


def filter_products(lat=None, lng=None, radius=None, count=10):
    filtered_products = current_app.products
    filtered_shops = None
    if lat and lng and radius:
        def distance_checker(shop):
            return distance(shop.lat, shop.lng, lat, lng) < radius
        filtered_shops = filter(distance_checker, current_app.shops)

    if filtered_shops:
        shop_ids = map(lambda shop: shop.id, filtered_shops)
        filtered_products = filter(
            lambda product: product.shop_id in shop_ids, filtered_products)
    return filtered_products[:count]


def distance(lat1, lng1, lat2, lng2):
    """Haversine formula for computing distance between two points in meters.
    """
    R = 6372795
    d_lng = math.radians(lng2 - lng1)
    rad_lat1 = math.radians(lat1)
    rad_lat2 = math.radians(lat2)
    sigma = 2 * math.asin(math.sqrt(
        math.sin((rad_lat2 - rad_lat1) / 2) ** 2 +
        math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lng / 2) ** 2))
    d = R * sigma
    return d


@api.route('/search', methods=['GET'])
def search():
    count = request.args.get('count', 10)
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    radius = request.args.get('radius')
    try:
        lat = float(lat)
        lng = float(lng)
        radius = int(radius)
    except Exception:
        lat, lng, radius = None, None, None
    try:
        count = int(count)
    except ValueError:
        count = 10
    filtered_products = filter_products(
        lat=lat, lng=lng, radius=radius,
        count=count)
    return jsonify({
        'products': map(prepare_product, filtered_products)
    })
