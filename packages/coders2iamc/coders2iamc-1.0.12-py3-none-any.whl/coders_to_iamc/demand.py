import json
from urllib.request import urlopen
import pandas as pd

from coders_to_iamc.constants import CODERS


def get_canadian_data(api_key: str, province: str, year: int):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/provincial_demand?key={api_key}&province={province}&year={year}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['local_time', 'demand_MWh', 'province']]
    melted = modeled_attributes.melt(id_vars=['local_time', 'province'], var_name='variable', value_name='value')

    melted['variable'] = 'Demand'
    melted.rename(columns={'province': 'region', 'local_time':'time'}, inplace=True)
    return melted

qc_lines = ['QC', 'QC(Highgate)', 'QC(HVDC)']

def get_us_data(api_key: str, province: str, year: int):
    """
    This function is used to get the technology parameter data from the CODERS API
    """
    with urlopen(f"{CODERS}/international_transfers?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    states_data = []
    province_line = qc_lines if province == 'QC' else [province]
    for p in province_line:
        states = modeled_attributes[modeled_attributes['province'] == p]['us_state'].unique()

        if len(states) == 0:
            return pd.DataFrame()

        for state in states:
            with urlopen(f"{CODERS}/international_transfers?key={api_key}&province={p}&us_state={state}&year={year}") as response:
                response_content = response.read()
                json_response = json.loads(response_content)
                state_df = pd.json_normalize(json_response)

            state_df = state_df[
                ['local_time', 'transfers_MWh', 'province']].copy()
            melted = state_df.melt(id_vars=['local_time', 'province'], var_name='variable', value_name='value')

            melted['variable'] = 'US Demand'
            melted.rename(columns={'province': 'region', 'local_time':'time'}, inplace=True)
            melted['region'] = province
            melted['region'] += '.b' if province == 'ON' and state == 'MISO' else '.a'
            states_data.append(melted)

    full_df = pd.concat(states_data)

    full_df = full_df.groupby(['time', 'region', 'variable']).sum().reset_index()
    return full_df


if __name__ == '__main__':
    api_key = ''
    df = get_us_data(api_key, 'QC', 2023)
