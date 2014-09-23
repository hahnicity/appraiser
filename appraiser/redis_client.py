from pickle import dumps, loads

from redis import StrictRedis


def get_all_redis_data():
    client = _get_client()
    keys = client.keys("*")
    return [loads(client.get(key)) for key in keys]


def write_data_to_redis(data):
    # Hardcoded for now
    client = _get_client()
    for entry in data:
        zpid = entry.pop("zpid")
        client.set(zpid, dumps(entry))


def _get_client():
    return StrictRedis(host="localhost", port=6379, db=0)
