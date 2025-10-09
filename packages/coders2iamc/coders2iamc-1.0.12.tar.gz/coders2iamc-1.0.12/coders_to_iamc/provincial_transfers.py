import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS



def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/transfer_capacities_copper?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['from_balancing_area', 'to_balancing_area', 'ttc_winter']
    ].rename(columns={'from_balancing_area': 'region', 'to_balancing_area': 'variable', 'ttc_winter': 'value'})

    modeled_attributes['region'] = modeled_attributes['region'].str.rstrip('.')
    modeled_attributes['variable'] = modeled_attributes['variable'].str.rstrip('.')

    modeled_attributes['variable'] = 'Inter-Provincial Transmission|Capacity|' + modeled_attributes['variable']
    return modeled_attributes


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
