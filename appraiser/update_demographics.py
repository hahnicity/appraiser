from cowboycushion.limiter import RedisLimiter
from flowzillow.client import ZillowClient

from appraiser.fetch_demographics import update_all_properties
from appraiser.redis_client import (
    get_client, get_all_redis_data, perform_redis_write, update_redis_entries
)


def main():
    # Mungy hardcoding for now
    redis_client = get_client()
    redis_data = get_all_redis_data(redis_client)[0:10]
    # XXX Put the limiter in before you begin full scale runs!!!
    # XXX Put the limiter in before you begin full scale runs!!!
    # XXX Put the limiter in before you begin full scale runs!!!
    zillow_client = ZillowClient("X1-ZWz1bvdg36cqvf_85kuc")
    # XXX Put the limiter in before you begin full scale runs!!!
    # XXX Put the limiter in before you begin full scale runs!!!
    # XXX Put the limiter in before you begin full scale runs!!!
    updated = update_all_properties(zillow_client, redis_data)
    perform_redis_write(updated, update_redis_entries)
