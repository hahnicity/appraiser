import re
from warnings import warn
from xml.etree import ElementTree


def _get_item_name(item):
    name = item.find("name").text
    name = name.replace(" ", "_").replace(".", "").replace("(", "").replace(")", "")
    # convert camel case to lowercase_with_underscores and convert to lowercase
    name = re.sub(r"([A-Z][a-z]+)([A-Z])", r"\1_\2", name).lower()
    # Convert letters-letters, numbers-letter, or letters-numbers to \1_\2
    name = re.sub(r"([A-Za-z])-([A-Za-z])", r"\1_\2", name)
    name = re.sub(r"(\d)-([A-Za-z])", r"\1_\2", name)
    name = re.sub(r"([A-Za-z])-(\d)", r"\1_\2", name)
    return name


def _get_data_point_value(data_point):
    for element in data_point:
        if element.tag == "values":
            for sub_elem in element:
                if sub_elem.tag not in ("city", "nation"):
                    warn("We found a sub element that was not in city or nation. It was\n\n{}"
                         "\n\nIn element with children{}".format(sub_elem.tag,
                                                                 element.get_children()))
            else:
                return element.find("city").find("value").text
        elif element.tag == "value":
            return element.text


def _parse_get_demographics(xml_tree):
    results = {}
    try:
        pages = xml_tree.find("response").find("pages")
        for page in pages:
            page_name = _get_item_name(page)
            results[page_name] = {}
            for table in page.find("tables"):
                table_name = _get_item_name(table)
                results[page_name][table_name] = {}
                for data_point in table.find("data"):
                    point_name = _get_item_name(data_point)
                    point_val = _get_data_point_value(data_point)
                    results[page_name][table_name][point_name] = point_val
    except (KeyError, IndexError):
        return None
    else:
        return results


def update_all_properties(zillow_client, data):
    all_properties = []
    cached_cities = []
    for entry in data:
        # This loops serves as persistent storage for cities during execution time.
        # Next step will be to get this data into redis
        updated, cached_cities = update_property(zillow_client, entry, cached_cities)
        all_properties.append(updated)
    filtered = filter(lambda entry: entry, all_properties)
    return filtered


def update_property(zillow_client, entry, cached_cities):
    def update_with_additional_data(data_entry, city_entry):
        try:
            affordability_stats = city_entry["affordability"]["affordability_data"]
            desired_stats = (
                "median_list_price",
                "median_sale_price",
                "median_single_family_home_value",
                "property_tax",
                "turnover_sold_within_last_yr"
            )
            for stat in desired_stats:
                data_entry[stat] = affordability_stats[stat]
        except KeyError as err:
            warn("The stat {} was unable to be found".format(err.message))
            return None
        else:
            return data_entry

    for city in cached_cities:
        if city[0] == entry["state"] and city[1] == entry["city"]:
            cached_data = city[2]
            updated = update_with_additional_data(entry, city[2])
            return updated, cached_cities
    else:
        demographics = zillow_client.get_demographics(state=entry["state"], city=entry["city"])
        xml_tree = ElementTree.fromstring(demographics)
        results = _parse_get_demographics(xml_tree)
        updated = update_with_additional_data(entry, results)
        cached_cities.append((entry["state"], entry["city"], results))
        return updated, cached_cities
