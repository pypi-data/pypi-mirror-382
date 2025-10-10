import datetime

# Logging utility to prepend an ISO 8601 timestamp to each log message.
def info(message):
    print("{}: {}".format(datetime.datetime.utcnow().isoformat(), message))

def warn(message):
    print("{}: {}".format(datetime.datetime.utcnow().isoformat(), message))

def error(message):
    print("{}: {}".format(datetime.datetime.utcnow().isoformat(), message))
