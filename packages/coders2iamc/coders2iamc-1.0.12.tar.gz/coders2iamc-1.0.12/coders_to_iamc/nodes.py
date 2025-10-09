import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'latitude': 'Nodes|Latitude|',
    'longitude': 'Nodes|Longitude|',
}



def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/nodes?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['node_code', 'latitude', 'longitude', 'copper_balancing_area']]
    melted = modeled_attributes.melt(id_vars=['node_code', 'copper_balancing_area'], var_name='variable', value_name='value')

    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['node_code']
    melted = melted.drop(columns=['node_code'])
    melted.rename(columns={'copper_balancing_area': 'region'}, inplace=True)
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
