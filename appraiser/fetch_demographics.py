from xml.etree import ElementTree


def _get_data_point_name(data_point):
    return data_point.find("name").text


def _get_data_point_value(data_point):
    for element in data_point:
        if element.tag == "values":
            for sub_elem in element:
                if sub_elem.tag not in ("city", "nation"):
                    import pdb
                    pdb.set_trace()
            else:
                return element.find("city").find("value").text
        elif element.tag == "value":
            return element.text


def _parse_get_demographics(xml_tree):
    results = {}
    try:
        pages = xml_tree.find("response").find("pages")
        for page in pages:
            page_name = page.find("name").text
            results[page_name] = {}
            for table in page.find("tables"):
                table_name = table.find("name").text
                results[page_name][table_name] = {}
                for data_point in table.find("data"):
                    point_name = _get_data_point_name(data_point)
                    point_val = _get_data_point_value(data_point)
                    results[page_name][table_name][point_name] = point_val
    except:
        import pdb
        pdb.set_trace()
        return None
    else:
        return results


def update_all_properties(zillow_client, data):
    updated = [update_property(zillow_client, entry) for entry in data]
    filtered = filter(lambda entry: entry, updated)
    return filtered


def update_property(zillow_client, entry):
    demographics = zillow_client.get_demographics(state=entry["state"], city=entry["city"])
    xml_tree = ElementTree.fromstring(demographics)
    results = _parse_get_demographics(xml_tree)
    import pdb; pdb.set_trace()
