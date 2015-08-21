# -*- coding: utf-8 -*-
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
    """Returns sorted tuple of products read form csv file.
    """
    products = []
    with open(data_path('products.csv')) as csvfile:
        reader = csv.reader(csvfile)
        schema = reader.next()
        Product = namedtuple('Product', schema)
        for line in reader:
            products.append(Product(
                line[0], line[1], line[2], float(line[3]), int(line[4])))
    products = tuple(sorted(products, key=lambda p: p.popularity, reverse=True))
    return products


def parse_shops():
    """Generates shops tuple and mapping from shop_id to index in that tuple.
    """
    shops = []
    shops_index = {}
    with open(data_path('shops.csv')) as csvfile:
        reader = csv.reader(csvfile)
        schema = reader.next()
        Shop = namedtuple('Shop', schema)
        for pos, line in enumerate(reader):
            shop = Shop(line[0], line[1], float(line[2]), float(line[3]))
            shops.append(shop)
            shops_index[shop.id] = pos
    shops = tuple(shops)
    return shops, shops_index


def parse_tags():
    """Makes mapping from tag_name to shop_ids by parsing tag-related
    .csv files.
    """
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


def filter_products(
        lat=None, lng=None, radius=None, tags=[], count=10, **kwargs):
    """Filters shops by distance and tags and then chooses most
    popular products from taht shops.
    """
    filtered_products = current_app.products[:count]
    check_distance = lat and lng and radius

    shop_ids = set()
    for tag in tags:
        shop_ids = shop_ids.union(current_app.tags.get(tag, set()))

    if check_distance:
        def distance_checker(shop):
            return distance(shop.lat, shop.lng, lat, lng) < radius
        filtered_shops = filter(distance_checker, current_app.shops)
        distance_shop_ids = map(lambda shop: shop.id, filtered_shops)
        if tags:
            shop_ids = shop_ids.intersection(distance_shop_ids)
        else:
            shop_ids = distance_shop_ids

    if check_distance or tags:
        filtered_products = filter_and_slice_products(shop_ids, count)
    return filtered_products


def filter_and_slice_products(shop_ids, count):
    """Filters only first :count: of products that are sold in shops
    from :shop_ids: list.
    """
    if not shop_ids:
        return []
    current = 0
    result = []
    for product in current_app.products:
        if current >= count:
            break
        if product.shop_id in shop_ids:
            result.append(product)
            current += 1
    return result


def distance(lat1, lng1, lat2, lng2):
    """Haversine formula for computing distance between two points in meters.
    """
    R = 6372795
    d_lng = math.radians(lng2 - lng1)
    rad_lat1 = math.radians(lat1)
    rad_lat2 = math.radians(lat2)
    sigma = 2 * math.asin(math.sqrt(
        math.sin((rad_lat2 - rad_lat1) / 2.) ** 2 +
        math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lng / 2.) ** 2))
    d = R * sigma
    return d


def validate_search_args(args):
    """Converts args to desired types if possible.
    """
    schema = [
        ('count', int),
        ('lat', float),
        ('lng', float),
        ('radius', int),
    ]
    result = {}
    for field, desired_type in schema:
        try:
            result[field] = desired_type(args.get(field))
        except Exception:
            pass
    tags = args.get('tags', None)
    if tags:
        result['tags'] = map(lambda tag: tag.strip(), tags.split(','))
    return result


@api.route('/search', methods=['GET'])
def search():
    params = validate_search_args(request.args)
    filtered_products = filter_products(**params)
    return jsonify({
        'products': map(prepare_product, filtered_products)
    })
