from flask import request, abort, make_response, jsonify
from botsislabutils import mysql_interface, config_manager, authentication_manager, authorization_manager

EMAIL_HEADER = 'NOT A REAL HEADER'
DEV_EMAIL = 'NOT A REAL EMAIL'

def get_username():
    return get_username_from_email(get_email())

def get_username_from_email(email):
    # Default to just the email address
    return email

def get_email():
    if '127.0.0.1' in request.host or 'localhost' in request.host or not config_manager.get_config('IS_SSO_ENABLED', '1') == '1':
        return DEV_EMAIL
    
    email = request.headers.get(EMAIL_HEADER, default = None)
    return email or None

def is_valid_user(username):
    query = '''
        SELECT username
        FROM user
        WHERE username = %s
        AND enabled = 1
    '''
    return mysql_interface.exists(query, (username,))

def require_valid_user():
    username = get_username()

    if username is None:
        abort(make_response(jsonify(message = 'No user is logged in'), 403))

    if not is_valid_user(username):
        abort(make_response(jsonify(message = 'User \'{}\' is not authorized'.format(username)), 403))

    print('User: {}'.format(username))

    return username

# Get a list of the users along with their enabled status and roles
def get_users(get_all_fields = False):
    fields_to_get = '*' if get_all_fields else 'username, enabled'
    query = '''
        SELECT {}
        FROM user
    '''.format(fields_to_get)
    users = mysql_interface.get_all_as_dicts(query)

    for user in users:
        user['roles'] = authorization_manager.get_roles(user['username'])

    return users

def set_user_enabled(username, enabled):
    query = '''
        UPDATE user
        SET enabled = %s
        WHERE username = %s
    '''
    mysql_interface.do_update(query, (enabled, username))

def add_user(username, roles, enabled):
    query = '''
        INSERT INTO user (username, enabled)
        VALUES (%s, %s)
    '''
    mysql_interface.do_update(query, (username, enabled))

    authorization_manager.set_roles(username, roles)

def delete_user(username):
    query = '''
        DELETE FROM user
        WHERE username = %s
    '''
    mysql_interface.do_update(query, (username,))

    query = '''
        DELETE FROM user_role
        WHERE username = %s
    '''
    mysql_interface.do_update(query, (username,))
