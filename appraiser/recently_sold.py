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
    return parse_results(results, zpid)


def parse_results(results, zpid):
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
            "sale_price": convert_str_to_float(results["sold"]),
            "zpid": zpid,
            "state": results["state"],
            "city": results["city"],
        }
    except KeyError:
        return None


def search_properties(latlong1, latlong2, **kwargs):
    searcher = SearchClient()
    args = (latlong1, latlong2)
    kwargs.update({"sort": "price", "lt": "000000", "status": "001000", "zoom": "12"})
    return searcher.search(*args, **kwargs)["map"]["properties"]


def gather_recently_sold_data(latlong1, latlong2, **kwargs):
    properties = search_properties(latlong1, latlong2, **kwargs)
    zpids = map(lambda home: home[0], properties)
    return get_zpid_info(zpids)
