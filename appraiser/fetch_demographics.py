from pickle import dumps, loads
import re
from warnings import warn
from xml.etree import ElementTree

from appraiser.constants import CITY_KEY


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


def _get_data_point_value(data_point, point_name):
    for element in data_point:
        if element.tag == "values":
            for sub_elem in element:
                if sub_elem.tag not in ("city", "nation"):
                    warn("We found a sub element that was not in city or nation. It was\n\n{}"
                         "\n\nIn element with children{}".format(sub_elem.tag,
                                                                 element.get_children()))
            else:
                city = element.find("city")
                if city is None:
                    warn("We could not find the city specific value for {} if this is a major "
                         "problem you may want to consider contacting zillow. We will return the "
                         "national value for this".format(point_name))
                else:
                    return city.find("value").text
                nation = element.find("nation")
                if nation is None:
                    warn("We could not find the national value for {}. If this is an issue it "
                         "might be best to contact Zillow. We will return None".format(point_name))
                    return None
                else:
                    return nation.find("value").text
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
                    point_val = _get_data_point_value(data_point, point_name)
                    results[page_name][table_name][point_name] = point_val
    except (KeyError, IndexError):
        return None
    else:
        return results


def update_all_properties(zillow_client, redis_client, data):
    all_properties = []
    cities_tmp = list(redis_client.smembers(CITY_KEY))
    cached_cities = [loads(city) for city in cities_tmp]
    for entry in data:
        # This loops serves as persistent storage for cities during execution time.
        # Next step will be to get this data into redis
        updated, cached_cities = update_property(zillow_client, redis_client, entry, cached_cities)
        all_properties.append(updated)
    filtered = filter(lambda entry: entry, all_properties)
    return filtered


def update_property(zillow_client, redis_client, entry, cached_cities):
    def update_with_additional_data(data_entry, city_entry):
        try:
            data_entry["affordability"] = city_entry["affordability"]["affordability_data"]
            data_entry["home_size"] = city_entry["homes_&_real_estate"]["census_summary_home_size"]
            data_entry["real_estate"] = city_entry["homes_&_real_estate"]["homes_&_real_estate_data"]
            data_entry["people"] = city_entry["people"]["people_data"]
            data_entry["relationship_status"] = city_entry["people"]["census_summary_relationship_status"]
        except KeyError as err:
            warn("The stat {} was unable to be found".format(err.message))
            return None
        else:
            return data_entry

    for city in cached_cities:
        if city["state"] == entry["state"] and city["city"] == entry["city"]:
            updated = update_with_additional_data(entry, city)
            return updated, cached_cities
    else:
        try:
            demographics = zillow_client.get_demographics(state=entry["state"], city=entry["city"])
            xml_tree = ElementTree.fromstring(demographics)
            results = _parse_get_demographics(xml_tree)
            results["state"] = entry["state"]
            results["city"] = entry["city"]
        except Exception:
            warn("We cannot parse data for {} because our xml may be malformed. If there is "
                 "a problem with this single API call just re-run this program and all missing "
                 "data will be populated. If this problem persists our xml parsing may be off "
                 "or there could be a server issue".format(entry["city"]))
            return None, cached_cities
        else:
            updated = update_with_additional_data(entry, results)
            cached_cities.append(results)
            redis_client.sadd(CITY_KEY, dumps(results))
            return updated, cached_cities
