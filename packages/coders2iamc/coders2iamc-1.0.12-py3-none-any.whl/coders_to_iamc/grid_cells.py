import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'longitude': 'Grid Cell|Longitude',
    'latitude': 'Grid Cell|Latitude',
    'province': 'Grid Cell|Province',
    'distance_to_grid': 'Grid Cell|Distance to Grid',
    'population': 'Grid Cell|Population',
    'surface_area_offshore': 'Grid Cell|Surface Area Offshore',
    'surface_area_onshore': 'Grid Cell|Surface Area Onshore',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"http://206.12.95.102/grid_cell_info?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)
    melted = modeled_attributes.melt(id_vars=['grid_cell', 'balancing_area'], var_name='variable', value_name='value').rename(columns={'balancing_area': 'region'})
    melted['variable'] = melted['variable'].map(mappings) + '|' + melted['grid_cell'].astype(str)
    melted = melted.drop(columns=['grid_cell'])
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
