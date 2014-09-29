from argparse import ArgumentParser

from appraiser.file_writer import write_data_to_file
from appraiser.recently_sold import gather_recently_sold_data
from appraiser.redis_client import (
    get_client, perform_redis_write, write_data_to_redis_if_not_exists
)

def rect_to_latlong(rect):
    latlong1 = rect.split(",")[0:2]
    latlong2 = rect.split(",")[2:]
    latlong1.reverse()
    latlong2.reverse()
    return latlong1, latlong2


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--store-to-file", action="store_true", help="Store to file otherwise store to redis"
    )
    parser.add_argument(
        "--rect",
        default="-122344866,37837310,-122228136,37891518",
        help="The coordinates for our housing search. The coords can be found by running a"
             " network trace on zillow",
    )
    parser.add_argument(
        "--clip-polygon", help="The custom clip polygon we can use for finding homes"
    )
    args = parser.parse_args()
    latlong1, latlong2 = rect_to_latlong(args.rect)
    if args.clip_polygon:
        data = gather_recently_sold_data(latlong1, latlong2, clipPolygon=args.clip_polygon)
    else:
        data = gather_recently_sold_data(latlong1, latlong2)
    if args.store_to_file:
        write_data_to_file(data)
    else:
        redis_client = get_client()
        perform_redis_write(redis_client, data, write_data_to_redis_if_not_exists)


if __name__ == "__main__":
    main()
