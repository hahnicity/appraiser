from cowboycushion.limiter import RedisLimiter
from flowzillow.client import ZillowClient

from appraiser.fetch_demographics import update_all_properties
from appraiser.redis_client import (
    get_client, get_all_redis_data, perform_redis_write, update_redis_entries
)


def main():
    # Mungy hardcoding for now
    redis_client = get_client()
    redis_data = get_all_redis_data(redis_client)
    zillow_client = RedisLimiter(
        ZillowClient("X1-ZWz1bvdg36cqvf_85kuc"),
        60,
        950,
        60 * 60 * 24,
        "localhost",
        6379,
        0
    )
    updated = update_all_properties(zillow_client, redis_client, redis_data)
    perform_redis_write(redis_client, updated, update_redis_entries)
