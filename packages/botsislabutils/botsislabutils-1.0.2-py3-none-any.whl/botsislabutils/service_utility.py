import json
import decimal
import datetime
import os
import random
import time
import traceback
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
from botsislabutils import authentication_manager
from botsislabutils import authorization_manager

# https://stackoverflow.com/questions/1960516/python-json-serialize-a-decimal-object
class DecimalEncoder(json.JSONEncoder):
    def default(self, o): # pylint: disable=E0202
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super(DecimalEncoder, self).default(o)

def add_error_handler(app):
    @app.errorhandler(Exception)
    def handle_error(error):
        message = str(error)
        code = 500

        print('Encountered error while processing request')
        print(traceback.format_exc())

        if isinstance(error, HTTPException):
            code = error.code
        elif isinstance(error, KeyError) or isinstance(error, TypeError):
            # Hide these embarrassing errors
            message = 'An unexpected error occurred'

        return jsonify(message = message), code

def add_no_cache_headers(app):
    @app.after_request
    def no_caching(response):
        response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, public, max-age=0')
        response.headers.set('Expires', '0')
        return response

def add_delayed_response(app):
    @app.after_request
    def delay_response(response):
        if os.getenv('FLASK_DEV_SERVER') == '1':
            if ('auth' in request.path):
                time.sleep(0.2)
            else:
                time.sleep(random.random() + 3)
        return response

def add_root_route(app, base_url):
    @app.route(base_url + '/')
    def root():
        return '''Root page'''

def add_auth_route(app, base_url):
    @app.route(base_url + '/auth', methods=['GET'])
    def is_authorized():
        username = authentication_manager.get_username()

        response = {
            'username': username,
            'roles': authorization_manager.get_roles(username)
        }

        if authentication_manager.is_valid_user(username):
            return jsonify(response)
        else:
            return jsonify(response), 403
