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
    with urlopen(f"http://206.12.95.102/generation_cost_evolution?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    columns = ['gen_type_copper']
    # keep any columns that start with a year
    columns.extend([col for col in modeled_attributes.columns if col.startswith('20')])
    modeled_attributes = modeled_attributes[columns]
    melted = modeled_attributes.melt(id_vars=['gen_type_copper'], var_name='time', value_name='value')
    melted['time'] = melted['time'].apply(lambda x: int(x[:4]))
    melted['variable'] = 'Generation Cost Evolution' + '|' + melted['gen_type_copper']
    melted = melted.drop(columns=['gen_type_copper'])
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
