import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'storage_facility_code': 'Hydro Pumped Storage|Facility Code|',
    'network_node_voltage': 'Hydro Pumped Storage|Network Node Voltage|',
    'distance_to_market_grid': 'Hydro Pumped Storage|Distance to Market Grid|',
    'facility_installed_capacity': 'Hydro Pumped Storage|Installed Capacity|',
    'minimum_generation': 'Hydro Pumped Storage|Minimum Generation|',
    'annualized_project_costs': 'Hydro Pumped Storage|Annualized Project Costs|',
    'fixed_om_costs': 'Hydro Pumped Storage|Fixed OM Costs|',
    'variable_om_costs': 'Hydro Pumped Storage|Variable OM Costs|',
    'development_time': 'Hydro Pumped Storage|Development Time|',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/hydro_pumped_storage?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['storage_facility_name', 'storage_facility_code',
         'copper_balancing_area', 'network_node_voltage', 'distance_to_market_grid', 'storage_type_copper',
         'facility_installed_capacity', 'minimum_generation', 'distance_to_market_grid', 'annualized_project_costs',
         'fixed_om_costs', 'variable_om_costs', 'development_time']
    ]

    melted = modeled_attributes.melt(id_vars=['storage_type_copper', 'storage_facility_name', 'copper_balancing_area'], var_name='variable', value_name='value')
    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['storage_type_copper'] + '|' + melted['storage_facility_name']
    melted = melted.rename(columns={'copper_balancing_area': 'region'})
    melted = melted.drop(columns=['storage_type_copper', 'storage_facility_name'])
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
