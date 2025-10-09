import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'startup_cost': 'Technology Parameter|Start Up Cost|',
    'shutdown_cost': 'Technology Parameter|Shut Down Cost|',
    'min_up_time_hours': 'Technology Parameter|Minimum Up Time|',
    'min_down_time_hours': 'Technology Parameter|Minimum Down Time|',
    'ramp_rate_percent_per_min': 'Technology Parameter|Ramp Rate|',
    'carbon_emissions': 'Technology Parameter|Carbon Intensity|',
    'min_plant_load': 'Technology Parameter|Minimum Plant Load|',
    'min_capacity_factor': 'Technology Parameter|Minimum Capacity Factor|',
    'max_capacity_factor': 'Technology Parameter|Maximum Capacity Factor|',
    'efficiency': 'Technology Parameter|Efficiency|',
    'fixed_om_costs': 'Technology Parameter|Fixed O&M Costs|',
    'variable_om_costs': 'Technology Parameter|Variable O&M Costs|',
    'annualized_capital_cost_CAD_per_kwyear': 'Technology Parameter|Annualized Capital Cost|',
    'average_fuel_price_CAD_per_MMBtu': 'Technology Parameter|Average Fuel Price|'
}

def get_data(api_key:str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/generation_generic?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['gen_type_copper', 'startup_cost', 'shutdown_cost', 'min_up_time_hours', 'min_down_time_hours',
         'ramp_rate_percent_per_min', 'carbon_emissions', 'min_plant_load', 'min_capacity_factor', 'max_capacity_factor',
         'efficiency', 'fixed_om_costs', 'variable_om_costs', 'annualized_capital_cost_CAD_per_kwyear', 'average_fuel_price_CAD_per_MMBtu']]

    melted = modeled_attributes.melt(id_vars=['gen_type_copper'], var_name='variable', value_name='value')
    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['gen_type_copper']
    melted = melted.drop(columns='gen_type_copper')
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)