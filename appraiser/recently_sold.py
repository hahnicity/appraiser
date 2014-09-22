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
    jobs = [pool.apply_async(get_data_set, args=(zpid,)) for zpid in zpids[1:40]]
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
    try:
        return {
            "use_code": {
                "Single Family": 0,
                "Condo":1,
                "Townhouse": 2,
                "Apartment": 3
            }[results["home_type"]],
            "year_built": int(results["year"]),
            "lot_sq_ft": float(results["lot"].replace("sqft", "").strip().replace(",", "")),
            "finished_sq_ft": float(results["sqft"].replace(",", "")),
            "bathrooms": float(results["bathrooms"]),
            "bedrooms": float(results["bedrooms"]),
            "total_rooms": float(results["room_count"]),
        }
    except KeyError:
        return None


def search_properties():
    searcher = SearchClient()
    # For now harcode these latlong vals to Oakland CA
    return searcher.search(
        (37683005, -122542534),
        (37901136, -121914940),
        sort="price",
        lt="000000",
        status="001000",  # Corresponds to all homes that were recently sold
        zoom="19"
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
        writer.writerow(data[0].keys())
        for entry in data:
            writer.writerow(entry.values())


def main():
    properties = search_properties()
    zpids = map(lambda home: home[0], properties)
    data_set = get_zpid_info(zpids)
    write_data_to_file(data_set)


if __name__ == "__main__":
    main()
