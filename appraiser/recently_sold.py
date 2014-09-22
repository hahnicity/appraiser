import csv
from multiprocessing import Pool

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
    try:
        return {
            "use_code": {
                "Single Family": 0,
                "Condo":1,
                "Townhouse": 2,
                "Apartment": 3
            }[results["home_type"]],
            "year_built": int(results["year"]),
            "lot_sq_ft": int(results["lot"].replace("sqft", "").strip().replace(",", "")),
            "finished_sq_ft": int(results["sqft"].replace(",", "")),
            "bathrooms": int(results["bathrooms"]),
            "bedrooms": int(results["bedrooms"]),
            "total_rooms": int(results["room_count"]),
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


def main():
    properties = search_properties()
    zpids = map(lambda home: home[0], properties)
    data_set = get_zpid_info(zpids)


if __name__ == "__main__":
    main()
