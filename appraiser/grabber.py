import csv
from xml.etree import ElementTree

from flowzillow.client import SearchClient, ZillowClient


def get_zpid_info(zillow_client, zpids):
    data_set = []
    for zpid in zpids[1:5]:
        response = zillow_client.get_z_estimate(zpid)
        street, zipcode = get_address_and_zip(response)
        deep_search = zillow_client.get_deep_search_results(street, zipcode)
        data = parse_deep_search(deep_search)
        if data:
            data_set.append(parse_deep_search(deep_search))
    import pdb
    pdb.set_trace()


def get_address_and_zip(raw_response):
    tree = ElementTree.fromstring(raw_response)
    response_node = tree.find("response")
    address_node = response_node.find("address")
    street_node = address_node.find("street")
    zipcode_node = address_node.find("zipcode")
    return street_node.text, zipcode_node.text


def parse_deep_search(search_response):
    tree = ElementTree.fromstring(search_response)
    response_node = tree.find("response")
    result_node = response_node[0][0]
    try:
        return {
            "use_code": result_node.find("useCode").text,
            "latitude": result_node.find("address").find("latitude").text,
            "longitude": result_node.find("address").find("longitude").text,
            "year_built": result_node.find("yearBuilt").text,
            "lot_sq_ft": result_node.find("lotSizeSqFt").text,
            "finished_sq_ft": result_node.find("finishedSqFt").text,
            "bathrooms": result_node.find("bathrooms").text,
            "bedrooms": result_node.find("bedrooms").text,
            "total_rooms": result_node.find("totalRooms").text,
            "tax_assessment": result_node.find("taxAssessment").text,
            "local_real_estate": result_node.find("localRealEstate")[0][0].text
        }
    except (AttributeError, IndexError):
        return None


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
