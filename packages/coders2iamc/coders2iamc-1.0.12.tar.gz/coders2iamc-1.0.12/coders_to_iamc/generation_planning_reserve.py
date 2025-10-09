import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'winter_wind': 'Planning Reserve|Wind|Winter',
    'winter_solar': 'Planning Reserve|Solar|Winter',
    'summer_wind': 'Planning Reserve|Wind|Summer',
    'summer_solar': 'Planning Reserve|Solar|Summer',
}


def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"http://206.12.95.102/generation_planning_reserve?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    melted = modeled_attributes.melt(id_vars=['province'],
                                     var_name='variable', value_name='value')

    melted['variable'] = melted['variable'].map(mappings)
    melted.rename(columns={'province': 'region'}, inplace=True)
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
