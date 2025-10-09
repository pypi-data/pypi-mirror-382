import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'reserve_requirements_percent': 'Reserve Requirements Percentage',
    'system_line_losses_percent': 'System Line Losses Percentage',
    'water_rentals_CAD_per_MWh': 'Water Rentals',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/transmission_generic?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['annualized_project_cost_CAD_per_MWkmyear', 'transmission_type']
    ].rename(columns={'annualized_project_cost_CAD_per_MWkmyear': 'value', 'transmission_type': 'variable'})
    modeled_attributes['variable'] = 'Annualized Project Cost|' + modeled_attributes['variable']
    return modeled_attributes


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
