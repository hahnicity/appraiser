from pickle import dumps, loads

from redis import StrictRedis


def get_all_redis_data(client):
    keys = client.keys("*_zpid")
    data = []
    for key in keys:
        entry = loads(client.get(key))
        entry["zpid"] = key.replace("_zpid", "")
        data.append(entry)
    return data


def perform_redis_write(client, data, func):
    for entry in data:
        zpid = entry.pop("zpid")
        key = "{}_zpid".format(zpid)
        func(client, entry, key)


def update_redis_entries(client, entry, key):
    if client.exists(key):
        client.set(key, dumps(entry))


def write_data_to_redis_if_not_exists(client, entry, key):
    if not client.exists(key):
        client.set(key, dumps(entry))


def get_client():
    # Hardcoded for now
    return StrictRedis(host="localhost", port=6379, db=0)
