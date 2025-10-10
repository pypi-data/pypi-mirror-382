from botsislabutils import authentication_manager, mysql_interface

def get_roles(username = None):
    if username is None:
        username = authentication_manager.get_username()

    query = "SELECT role FROM user_role WHERE username = %s"

    roles = mysql_interface.get_all_as_dicts(query, (username,))

    if roles is None:
        return []

    return [role['role'] for role in roles]

def has_role(role):
    user_roles = get_roles()
    return role in user_roles

def has_any_role(roles_to_check):
    user_roles = get_roles()
    return any(role in roles_to_check for role in user_roles)

def set_roles(username, roles):
    query = "DELETE FROM user_role WHERE username = %s"
    mysql_interface.do_update(query, (username,))

    query = "INSERT INTO user_role (username, role) VALUES (%s, %s)"
    for role in roles:
        mysql_interface.do_update(query, (username, role))

# TODO Want to be able to keep track of what roles can do what
# CREATE TABLE role (
#     role_id VARCHAR(255) NOT NULL,
#     label VARCHAR(255) NOT NULL,
#     PRIMARY KEY (role_id)
# );

# CREATE TABLE permission (
#     permission_id VARCHAR(255) NOT NULL,
#     name VARCHAR(255) NOT NULL,
#     PRIMARY KEY (permission_id)
# );

# CREATE TABLE role_permission (
#     role_id VARCHAR(255) NOT NULL,
#     permission_id VARCHAR(255) NOT NULL,
#     PRIMARY KEY (role_id, permission_id),
#     FOREIGN KEY (role_id) REFERENCES role(role_id)
# );
