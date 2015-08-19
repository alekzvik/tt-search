# -*- coding: utf-8 -*-
import random
import string

from flask import Blueprint, current_app, jsonify
from flask.ext.cors import CORS

api = Blueprint('api', __name__)
CORS(api)


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)


def generate_dummy_product_data():
    return {
        'shop': {
            'lat': 59 + random.uniform(0, 0.5),
            'lng': 17.5 + random.random(),
            'name': ''.join(random.sample(string.ascii_letters, 7))},
        'popularity': random.random(),
        'name': ''.join(random.sample(string.ascii_letters, 8)),
    }


@api.route('/search', methods=['GET'])
def search():
    products = [generate_dummy_product_data() for _ in range(25)]
    return jsonify({'products': products[:20]})
