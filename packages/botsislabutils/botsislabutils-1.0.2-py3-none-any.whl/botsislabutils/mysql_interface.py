import os
from datetime import datetime
import traceback
import mysql.connector
from mysql.connector import errorcode

connection = None
REUSE_CONNECTION = True

def get_connection():
    if REUSE_CONNECTION:
        global connection
        # Create a new connection if there is no connection or the connection is closed
        if connection is None:
            connection = create_connection()
            print('CONNECTION CREATED:', connection.connection_id)
        elif not connection.is_connected():
            connection = create_connection()
            print('CONNECTION RE-CREATED:', connection.connection_id)
        return connection
    else:
        return create_connection()

def create_connection():
    return mysql.connector.connect(
        user = os.getenv('DATABASE_USER', 'root'),
        password = os.getenv('DATABASE_PASS', 'password'),
        host = os.getenv('DATABASE_HOST', 'localhost'),
        port = os.getenv('DATABASE_PORT', '3306'),
        database = os.getenv('DATABASE_SCHEMA_NAME', 'infovip'),
        ssl_disabled = True,
        autocommit = True
    )

def close_connection_if_not_reused(connection = None):
    if connection is not None and not REUSE_CONNECTION:
        connection.close()

def query_one(query, params):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    close_connection_if_not_reused(connection)
    return result

def get_single_value(query, params = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    close_connection_if_not_reused(connection)
    return result[0][0] if result else None

def get_all(table_name):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM ' + table_name)
    results = cursor.fetchall()
    cursor.close()
    close_connection_if_not_reused(connection)
    return results

def get_all_as_rows(query, params = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    close_connection_if_not_reused(connection)
    return results

def get_one(table_name, where_columns, where_values):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    where_clause = get_where_clause(where_columns)
    query = 'SELECT * FROM ' + table_name + ' ' + where_clause
    cursor.execute(query, where_values)
    result = cursor.fetchone()
    cursor.close()
    close_connection_if_not_reused(connection)
    return result

def get_rows_where(table_name, where_columns, where_values):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    where_clause = get_where_clause(where_columns)
    query = 'SELECT * FROM ' + table_name + ' ' + where_clause
    cursor.execute(query, where_values)
    result = cursor.fetchall()
    cursor.close()
    close_connection_if_not_reused(connection)
    return result

def update(table_name, update_map, where_map):
    set_clause = get_set_pairs_string(update_map.keys())
    where_clause = get_where_clause(where_map.keys())
    query = 'UPDATE %s SET %s %s' % (table_name, set_clause, where_clause)
    params = tuple(update_map.values()) + tuple(where_map.values())
    do_update(query, params)

def get_where_clause(where_columns):
    where_clause = ''

    for index, column in enumerate(where_columns):
        where_clause += 'WHERE ' if index == 0 else 'AND '
        where_clause += column + ' = %s '

    return where_clause

def get_set_pairs_string(update_columns):
    set_pairs_strings = []

    for column in update_columns:
        set_pairs_strings.append(column + ' = %s')

    return ', '.join(set_pairs_strings)

# Insert or update rows and return the last row id (primary key) or the number of rows updated
def do_update(query, params = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    if cursor.lastrowid:
        result = cursor.lastrowid
    else:
        result = cursor.rowcount
    connection.commit()
    cursor.close()
    close_connection_if_not_reused(connection)
    return result

# Update multiple rows with the same query and different parameters
def do_update_many(query, params_list, connection = None):
    conn_is_temporary = connection is None
    if conn_is_temporary:
        connection = get_connection()
    cursor = connection.cursor()
    cursor.executemany(query, params_list)
    num_updated = cursor.rowcount
    if conn_is_temporary:
        connection.commit()
        cursor.close()
    close_connection_if_not_reused(connection)
    return num_updated

# Return the first row as a dictionary
def get_one_as_dict(query, params = ()):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    close_connection_if_not_reused(connection)
    return result

# Return all rows as dictionaries
def get_all_as_dicts(query, params = ()):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    close_connection_if_not_reused(connection)
    return results

# Return whether the select query returns any result
def exists(query, params = ()):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    close_connection_if_not_reused(connection)
    return len(results) > 0

def get_in_list(n_entries):
    if n_entries < 1:
        raise ValueError("n_entries must be a positive integer to build a list for SQL query")
    ret = "("
    ret += "%s, " * (n_entries - 1)
    ret += "%s)"
    return ret

def insert_log_entry(container_type, container_id, message, target):
    query = "INSERT INTO pipeline_log (container_type, container_id, message, target) VALUES (%s, %s, %s, %s)"
    params = (container_type, container_id, message, target)
    do_update(query, params)


class DeadlockRedoer():
    def __init__(self, max_retries):
        self.max_retries = max_retries

    def do(self, func, *args, **kwargs):
        for curr_iter in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except mysql.connector.Error as err:
                function_name = func.__name__
                if err.errno == errorcode.ER_LOCK_DEADLOCK:
                    if curr_iter < self.max_retries - 1:
                        print("{0}: Warning: MySQL deadlock error encountered when calling {1}. Retrying.".format(datetime.now(), function_name))
                    else:
                        print("{0}: Error: MySQL deadlock error encountered when calling {1}. Max retries ({2}) exceeded.".format(datetime.now(), function_name, self.max_retries))
                        raise err
                else:
                    print("{0}: Exception when calling {1}".format(datetime.now(), function_name))
                    print(traceback.format_exc())
                    break


# Class to make it easier to work with transactions
class Transaction():
    def __init__(self):
        self.connection = get_connection()
        
    def __enter__(self):
        # Disable autocommit
        self.connection.autocommit = False
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()

        # Re-enable autocommit
        self.connection.autocommit = True

        return False
