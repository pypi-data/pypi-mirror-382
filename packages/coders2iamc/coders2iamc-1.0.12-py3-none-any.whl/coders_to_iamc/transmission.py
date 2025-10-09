import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS

mappings = {
    'network_node_code_starting': 'Intra-Provincial Transmission|Start Node|',
    'network_node_code_ending': 'Intra-Provincial Transmission|End Node|',
    'ttc_winter': 'Intra-Provincial Transmission|Capacity|',
    'Transmission_Line_Segment_Reactance': 'Intra-Provincial Transmission|Reactance|',
}



def get_data(api_key: str):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/transmission_lines?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['transmission_line_id', 'network_node_code_starting', 'network_node_code_ending', 'ttc_winter', 'Transmission_Line_Segment_Reactance',
         'province']]
    melted = modeled_attributes.melt(id_vars=['transmission_line_id', 'province'], var_name='variable', value_name='value')

    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['transmission_line_id'].astype(str)
    melted = melted.drop(columns=['transmission_line_id'])
    melted.rename(columns={'province': 'region'}, inplace=True)
    return melted


if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
