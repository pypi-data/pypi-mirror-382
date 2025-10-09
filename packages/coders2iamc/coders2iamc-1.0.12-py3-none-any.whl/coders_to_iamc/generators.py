import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS, gen_type_copper_mapping

mappings = {
    'latitude': 'Generators|Latitude|',
    'longitude': 'Generators|Longitude|',
    'unit_installed_capacity': 'Generators|Capacity|',
    'network_node_code': 'Generators|Node Code|',
    'previous_renewal_year': 'Generators|Previous Renewal Year|',
    'possible_renewal_year': 'Generators|Possible Renewal Year|',
    'closure_year': 'Generators|Closure Year|',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/generators?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)
    
    modeled_attributes['gen_type_copper'] = modeled_attributes['gen_type'].map(gen_type_copper_mapping)

    modeled_attributes = modeled_attributes[
        ['generation_unit_code', 'gen_type_copper', 'copper_balancing_area', 'latitude', 'longitude', 'unit_installed_capacity',
         'network_node_code', 'start_year', 'previous_renewal_year', 'possible_renewal_year', 'closure_year']]
    melted = modeled_attributes.melt(id_vars=['gen_type_copper', 'generation_unit_code', 'copper_balancing_area', 'start_year'],
                                     var_name='variable', value_name='value')

    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['gen_type_copper'] + '|' + melted['generation_unit_code'] + '|' + \
                         melted['start_year'].astype(str)
    melted = melted.drop(columns=['gen_type_copper', 'generation_unit_code', 'start_year'])
    melted.rename(columns={'copper_balancing_area': 'region'}, inplace=True)
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
