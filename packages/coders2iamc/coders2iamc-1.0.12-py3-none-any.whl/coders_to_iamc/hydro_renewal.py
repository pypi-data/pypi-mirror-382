import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'renewal_facility_code': 'Hydro Renewal|Facility Code|',
    'network_node_voltage': 'Hydro Renewal|Network Node Voltage|',
    'distance_to_market_grid': 'Hydro Renewal|Distance to Market Grid|',
    'facility_installed_capacity': 'Hydro Renewal|Installed Capacity|',
    'minimum_generation': 'Hydro Renewal|Minimum Generation|',
    'annualized_project_costs': 'Hydro Renewal|Annualized Project Costs|',
    'fixed_om_costs': 'Hydro Renewal|Fixed OM Costs|',
    'variable_om_costs': 'Hydro Renewal|Variable OM Costs|',
    'development_time': 'Hydro Renewal|Development Time|',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/hydro_renewal?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['renewal_facility_name', 'renewal_facility_code',
         'copper_balancing_area', 'network_node_voltage', 'distance_to_market_grid', 'gen_type_copper',
         'facility_installed_capacity', 'minimum_generation', 'distance_to_market_grid', 'annualized_project_costs',
         'fixed_om_costs', 'variable_om_costs', 'development_time','facility_installed_capacity']
    ]

    melted = modeled_attributes.melt(id_vars=['gen_type_copper', 'renewal_facility_name', 'copper_balancing_area'], var_name='variable', value_name='value')
    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['gen_type_copper'] + '|' + melted['renewal_facility_name']
    melted = melted.rename(columns={'copper_balancing_area': 'region'})
    melted = melted.drop(columns=['gen_type_copper', 'renewal_facility_name'])
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
