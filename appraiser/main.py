from argparse import ArgumentParser

from appraiser.file_writer import write_data_to_file
from appraiser.recently_sold import gather_recently_sold_data
from appraiser.redis_client import write_data_to_redis


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
        write_data_to_redis(data)


if __name__ == "__main__":
    main()
