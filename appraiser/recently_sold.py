from multiprocessing import Pool

from flowzillow.client import SearchClient
from requests.exceptions import ConnectionError, Timeout
from scrapezillow.scraper import scrape_url


def get_zpid_info(zpids):
    """
    Get all the home data we requested.

    Our multiprocessing setup here is a bit more complicated because we don't
    want to explicitly fail if we receive an error.
    """
    pool = Pool(200)
    jobs = [pool.apply_async(get_result, args=(zpid,)) for zpid in zpids]
    pool.close()
    data = []
    for job in jobs:
        try:
            data.append(job.get())
        except (ConnectionError, Timeout):
            continue
    pool.join()
    return filter(lambda data: data is not None, data)


def get_result(zpid):
    result = scrape_url(None, zpid, 5)
    result["zpid"] = zpid
    return result


def search_properties(latlong1, latlong2, **kwargs):
    searcher = SearchClient()
    args = (latlong1, latlong2)
    kwargs.update({"sort": "price", "lt": "000000", "status": "001000", "zoom": "12"})
    return searcher.search(*args, **kwargs)["map"]["properties"]


def gather_recently_sold_data(latlong1, latlong2, **kwargs):
    properties = search_properties(latlong1, latlong2, **kwargs)
    zpids = map(lambda home: home[0], properties)
    return get_zpid_info(zpids)
