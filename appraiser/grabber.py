import csv
from xml.etree import ElementTree

from flowzillow.client import SearchClient, ZillowClient


def get_zpid_info(zillow_client, zpids):
    for zpid in zpids:
        response = zillow_client.get_z_estimate(zpid)
        street, zipcode = get_address_and_zip(response)
        deep_search = zillow_client.get_deep_search_results(street, zipcode)
        import pdb
        pdb.set_trace()


def get_address_and_zip(raw_response):
    tree = ElementTree.fromstring(raw_response)
    response_node = tree.find("response")
    address_node = response_node.find("address")
    street_node = address_node.find("street")
    zipcode_node = address_node.find("zipcode")
    return street_node.text, zipcode_node.text


def search_properties():
    searcher = SearchClient()
    # For now harcode these latlong vals to Oakland CA
    return searcher.search(
        (37683005, -122542534),
        (37901136, -121914940),
        sort="price",
        lt="000000",
        status="001000",
        zoom="19"
    )["map"]["properties"]


def main():
    client = ZillowClient("X1-ZWz1b3t7fn7dvv_5cfwc")
    properties = search_properties()
    zpids = map(lambda home: home[0], properties)
    get_zpid_info(client, zpids)


if __name__ == "__main__":
    main()
