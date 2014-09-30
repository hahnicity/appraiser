import csv
from datetime import datetime
import os
import shutil

from appraiser.redis_client import get_all_redis_data, get_client


def archive_previous_files(appraiser_dir, home_data_file):
    if os.path.exists(home_data_file):
        archive_dir = os.path.join(appraiser_dir, "archive_dir")
        try:
            os.mkdir(archive_dir)
        except OSError:
            pass
        shutil.copyfile(
            home_data_file,
            os.path.join(archive_dir, "{}-{}".format(
                datetime.now().strftime("%Y-%m-%d-%H-%M"), "home-data.csv")
            )
        )


def filter_entries_before_write(data):
    """
    Filter out any unnecessary data from our data entries like zpid, city, state, etc.
    """
    tmp_data = list(data)
    new_data = []
    for entry in tmp_data:
        del entry["zpid"]
        del entry["state"]
        del entry["city"]
        new_data.append(entry)
    return new_data


def strict_data_orderer(entry, ordering):
    """
    This function ensures all features will be in the correct order when we write to file.
    """
    return [entry[key] for key in ordering]


def write_data_to_file(data):
    appraiser_dir = os.path.dirname(__file__)
    home_data_file = os.path.join(appraiser_dir, "home-data.csv")
    archive_previous_files(appraiser_dir, home_data_file)
    with open(home_data_file, "w") as file_:
        writer = csv.writer(file_)
        header = data[0].keys()
        header[0] = "#{}".format(header[0])
        sale_price_index = header.index("sale_price")
        header.insert(len(header), header.pop(sale_price_index))
        writer.writerow(header)
        for entry in data:
            values = strict_data_orderer(entry, data[0].keys())
            values.insert(len(values), values.pop(sale_price_index))
            writer.writerow(values)


def main():
    redis_client = get_client()
    data = get_all_redis_data(redis_client)
    data = filter_entries_before_write(data)
    write_data_to_file(data)
