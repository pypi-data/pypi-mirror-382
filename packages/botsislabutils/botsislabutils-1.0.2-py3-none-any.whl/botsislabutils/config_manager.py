from botsislabutils import mysql_interface, logger

def get_int_config(key, default):
    value = get_config(key, default)
    try:
        return int(value)
    except ValueError:
        logger.error("Could not convert configuration value {} for key {} to an integer. Using default value {}.".format(value, key, default))
        return default

# Note: not catching exceptions here because we want to know if there is a problem
# with the database connection. The absence of a configuration value is already handled.
def get_config(key, default):
    query = "SELECT `value` FROM configuration WHERE `key` = %s"
    config = mysql_interface.get_one_as_dict(query, (key,))
    if config is not None:
        return config['value']
    else:
        return default

def parse_boolean(value):
    """
    For reading environment variables. If the value is a zero, then it usually comes
    in as the string value "0" which is truth-y.  It needs a special parsing to
    confirm that it is False.
    """
    
    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return value != 0
    elif isinstance(value, str):
        if value in ["T", "t", "TRUE", "True", "true"]:
            return True
        if value in ["F", "f", "FALSE", "False", "false"]:
            return False
        try:
            as_int = int(value)
            return as_int != 0
        except ValueError:
            return bool(value)
    else:
        return bool(value)
