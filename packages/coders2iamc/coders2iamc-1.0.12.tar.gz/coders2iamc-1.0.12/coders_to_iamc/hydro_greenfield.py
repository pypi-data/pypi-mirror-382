import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'greenfield_facility_code': 'Hydro Greenfield|Facility Code|',
    'network_node_voltage': 'Hydro Greenfield|Network Node Voltage|',
    'distance_to_market_grid': 'Hydro Greenfield|Distance to Market Grid|',
    'facility_installed_capacity': 'Hydro Greenfield|Installed Capacity|',
    'minimum_generation': 'Hydro Greenfield|Minimum Generation|',
    'annualized_project_costs': 'Hydro Greenfield|Annualized Project Costs|',
    'fixed_om_costs': 'Hydro Greenfield|Fixed OM Costs|',
    'variable_om_costs': 'Hydro Greenfield|Variable OM Costs|',
    'development_time': 'Hydro Greenfield|Development Time|',
    'capacity_factor': 'Technology Parameter|Greenfield Capacity Factor|'
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/hydro_greenfield?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['greenfield_facility_name', 'greenfield_facility_code',
         'copper_balancing_area', 'network_node_voltage', 'distance_to_market_grid', 'gen_type_copper',
         'facility_installed_capacity', 'minimum_generation', 'distance_to_market_grid', 'annualized_project_costs',
         'fixed_om_costs', 'variable_om_costs', 'development_time', 'capacity_factor']
    ]

    melted = modeled_attributes.melt(id_vars=['gen_type_copper', 'greenfield_facility_name', 'copper_balancing_area'], var_name='variable', value_name='value')
    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['gen_type_copper'] + '|' + melted['greenfield_facility_name']
    melted = melted.rename(columns={'copper_balancing_area': 'region'})
    melted = melted.drop(columns=['gen_type_copper', 'greenfield_facility_name'])
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
