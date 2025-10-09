import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS, gen_type_copper_mapping

mappings = {
    'latitude': 'Generators|Latitude|',
    'longitude': 'Generators|Longitude|',
    'storage_capacity': 'Generators|Capacity|',
    'storage_energy': 'Generators|Storage Energy|',
    'network_node_code': 'Generators|Node Code|',
    'previous_renewal_year': 'Generators|Previous Renewal Year|',
    'possible_renewal_year': 'Generators|Possible Renewal Year|',
    'closure_year': 'Generators|Closure Year|',
}

def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/storage?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)
    
    modeled_attributes['storage_type_copper'] = modeled_attributes['storage_type'].map(gen_type_copper_mapping)

    modeled_attributes = modeled_attributes[
        ['storage_facility_code', 'storage_type_copper', 'storage_capacity', 'storage_energy', 'network_node_code',
         'copper_balancing_area', 'latitude', 'longitude', 'start_year', 'previous_renewal_year', 'possible_renewal_year', 'closure_year']]

    melted = modeled_attributes.melt(id_vars=['storage_type_copper', 'storage_facility_code', 'copper_balancing_area', 'start_year'],
                                     var_name='variable', value_name='value')

    
    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['storage_type_copper'] + '|' + melted[
        'storage_facility_code'] + '|' + melted['start_year'].astype(str)
    melted = melted.drop(columns=['storage_type_copper', 'storage_facility_code', 'start_year'])
    melted.rename(columns={'copper_balancing_area': 'region'}, inplace=True)

    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
