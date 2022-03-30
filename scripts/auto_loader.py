import json
import os

CUR_MODULE_DIR = os.path.dirname(__file__)
print(CUR_MODULE_DIR)

def load_from_file(file_name=None):
    if file_name:
        file_path = os.path.join(CUR_MODULE_DIR, file_name+".json")

    if not os.path.isfile(file_path):
        raise Exception("{0} not found at {1}".format(file_name, file_path))

    with open(file_path) as json_data:
        return json.load(json_data)
