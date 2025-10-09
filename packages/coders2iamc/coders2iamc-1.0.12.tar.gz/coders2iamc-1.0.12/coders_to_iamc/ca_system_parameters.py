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
    with urlopen(f"http://206.12.95.102/CA_system_parameters?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes.drop(columns=['notes'])

    melted = modeled_attributes.melt(id_vars=['province'], var_name='variable', value_name='value')
    melted['variable'] = melted['variable'].map(mappings)
    melted = melted.rename(columns={'province': 'region'})
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
