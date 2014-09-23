import csv
from datetime import datetime
import os
import shutil


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
        zpid_index = header.index("zpid") if "zpid" in header else None
        writer.writerow(header)
        for entry in data:
            values = entry.values()
            values.insert(len(values), values.pop(sale_price_index))
            if zpid_index:
                del values[zpid_index]
            writer.writerow(values)
