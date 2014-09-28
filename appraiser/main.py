from argparse import ArgumentParser

from appraiser.file_writer import write_data_to_file
from appraiser.recently_sold import gather_recently_sold_data
from appraiser.redis_client import (
    get_client, perform_redis_write, write_data_to_redis_if_not_exists
)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--store-to-file", action="store_true", help="Store to file otherwise store to redis"
    )
    args = parser.parse_args()
    data = gather_recently_sold_data()
    if args.store_to_file:
        write_data_to_file(data)
    else:
        redis_client = get_client()
        perform_redis_write(redis_client, data, write_data_to_redis_if_not_exists)


if __name__ == "__main__":
    main()
