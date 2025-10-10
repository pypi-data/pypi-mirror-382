from nepali_toolkit.common.util import read_json_resource

def load_month_table():
    return read_json_resource("nepali_toolkit.bs.data", "bs_years_2077_2082.json")
