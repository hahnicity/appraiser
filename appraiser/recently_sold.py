import csv
from datetime import datetime
from multiprocessing import Pool
import os
import shutil

from flowzillow.client import SearchClient
from scrapezillow.scraper import scrape_url


def get_zpid_info(zpids):
    """
    Get all the home data we requested.

    Our multiprocessing setup here is a bit more complicated because we don't
    want to explicitly fail if we receive an error.
    """
    pool = Pool(200)
    jobs = [pool.apply_async(get_data_set, args=(zpid,)) for zpid in zpids]
    pool.close()
    data = []
    for job in jobs:
        try:
            data.append(job.get())
        except Exception as e:
            continue
    pool.join()
    return filter(lambda data: data is not None, data)


def get_data_set(zpid):
    results = scrape_url(None, zpid, 5)
    return parse_results(results)


def parse_results(results):
    def convert_str_to_float(str_):
        return float(str_.strip().replace(",", ""))

    try:
        if results["home_type"] != "Single Family":
            return None
        return {
            "year_built": int(results["year"]),
            "lot_sq_ft": convert_str_to_float(results["lot"].replace("sqft", "")),
            "finished_sq_ft": convert_str_to_float(results["sqft"]),
            "bathrooms": float(results["bathrooms"]),
            "bedrooms": float(results["bedrooms"]),
            "total_rooms": float(results["room_count"]),
            "sale_price": convert_str_to_float(results["sold"])
        }
    except KeyError:
        return None


def search_properties():
    searcher = SearchClient()
    # For now harcode these latlong vals
    return searcher.search(
        (37869179, -122293861),
        (37882729, -122264678),
        sort="price",
        lt="000000",
        status="001000",  # Corresponds to all homes that were recently sold
        zoom="12",
        rect="-122344866,37837310,-122228136,37891518",
        clipPolygon="37.855406,-122.266417|37.852289,-122.287016|37.854187,-122.287016|37.865029,-122.292166|37.876412,-122.294054|37.875328,-122.294054|37.875328,-122.291651|37.876954,-122.284956|37.877089,-122.277575|37.878309,-122.27191|37.878309,-122.268991|37.855406,-122.266073|37.855406,-122.266417|37.855406,-122.266417"
    )["map"]["properties"]


def write_data_to_file(data):
    appraiser_dir = os.path.dirname(__file__)
    home_data_file = os.path.join(appraiser_dir, "home-data.csv")
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
    with open(home_data_file, "w") as file_:
        writer = csv.writer(file_)
        header = data[0].keys()
        header[0] = "#{}".format(header[0])
        sale_price_index = header.index("sale_price")
        header.insert(len(header), header.pop(sale_price_index))
        writer.writerow(header)
        for entry in data:
            values = entry.values()
            values.insert(len(values), values.pop(sale_price_index))
            writer.writerow(values)


def main():
    properties = search_properties()
    zpids = map(lambda home: home[0], properties)
    data_set = get_zpid_info(zpids)
    write_data_to_file(data_set)


if __name__ == "__main__":
    main()
