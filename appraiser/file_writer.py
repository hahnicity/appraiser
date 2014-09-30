"""
The final step of our data aggregation process. Take all the data from redis and write it
to a file so we can trivially (for now) load it from octave.
"""
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
    def convert_str_to_float(str_):
        return float(str_.strip().replace(",", ""))

    def get_lot_size(size):
        size = size.replace("sqft", "")
        if "acres" in size:
            return float(size.split(" ")[0]) * 43560
        else:
            return convert_str_to_float(size)

    tmp_data = list(data)
    new_data = []
    for entry in tmp_data:
        try:
            if entry["home_type"] != "Single Family":
                continue
            new_entry = {
                "year_built": int(entry["year"]),
                "lot_sq_ft": get_lot_size(entry["lot"]),
                "finished_sq_ft": convert_str_to_float(entry["sqft"]),
                "bathrooms": float(entry["bathrooms"]),
                "bedrooms": float(entry["bedrooms"]),
                "total_rooms": float(entry["room_count"]),
                "sale_price": convert_str_to_float(entry["sold"]),
                "married_male": convert_str_to_float(entry["relationship_status"]["married_male"]),
                "married_female": convert_str_to_float(entry["relationship_status"]["married_female"]),
                "single_male": convert_str_to_float(entry["relationship_status"]["single_male"]),
                "single_female": convert_str_to_float(entry["relationship_status"]["single_female"]),
                "median_income": convert_str_to_float(entry["people"]["median_household_income"]),
                "median_age": convert_str_to_float(entry["people"]["median_age"]),
                "median_sale_price": convert_str_to_float(entry["affordability"]["median_sale_price"]),
                "median_single_family_home_value": convert_str_to_float(entry["affordability"]["median_single_family_home_value"]),
                "turnover": convert_str_to_float(entry["affordability"]["turnover_sold_within_last_yr"]),
                "property_tax": convert_str_to_float(entry["affordability"]["property_tax"]),
                "single_family_homes": convert_str_to_float(entry["real_estate"]["single_family_homes"]),
                "median_home_size": convert_str_to_float(entry["real_estate"]["median_home_size_sq_ft"]),
            }
            new_entry["income_to_median_sale_price"] = new_entry["median_income"] / new_entry["median_sale_price"]
            new_entry["size_to_median_size"] = new_entry["finished_sq_ft"] / new_entry["median_home_size"]
            # Start comparing bedrooms to median bedroom values
        except KeyError:
            continue
        else:
            new_data.append(new_entry)
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
