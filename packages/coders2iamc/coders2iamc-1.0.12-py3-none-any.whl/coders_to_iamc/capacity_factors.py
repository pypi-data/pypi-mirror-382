import json
from urllib.request import urlopen
import pandas as pd


def get_hydro_data(api_key: str, province, year):
    """
    This function is used to get the hydro capacity factor data from the CODERS API
    """
    with urlopen(f"http://206.12.95.102/hydro_capacity_factor?key={api_key}&province={province}&year={year}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['province', 'local_time', 'capacity_factor']]
    melted = modeled_attributes.melt(id_vars=['local_time', 'province'], var_name='variable', value_name='value')

    melted['variable'] = 'Hydro Capacity Factor'
    melted.rename(columns={'province': 'region', 'local_time':'time'}, inplace=True)
    return melted

def get_wind_solar_data(api_key: str, year):
    """
    This function is used to get the VRE capacity factor data from the CODERS API
    """
    with urlopen(f"http://206.12.95.102/grid_cell_info?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        grid_cell = pd.json_normalize(json_response)
        grid_cell = grid_cell[['longitude', 'latitude', 'balancing_area','grid_cell']]


    wind = pd.read_csv(f'http://206.12.95.102/wind_capacity_factor?year=2021&key={api_key}&year={year}', index_col=0)
    wind.index = wind.index-1
    wind.index = pd.to_datetime(year, format='%Y') + pd.to_timedelta(wind.index, unit='h')

    wind = wind.T
    wind.index = wind.index.astype(int)
    wind = pd.merge(wind, grid_cell, left_index=True, right_on='grid_cell')
    wind['variable'] = 'VRE Capacity Factor|Wind|' + wind['grid_cell'].astype(str) + '|' + wind['latitude'].astype(str) + '_' + wind['longitude'].astype(str)
    wind = wind.drop(columns=['latitude', 'longitude','grid_cell'])
    wind.rename(columns={'balancing_area': 'region'}, inplace=True)

    wind_melted = wind.melt(id_vars=['variable', 'region'], var_name='time', value_name='value')


    solar = pd.read_csv(f'http://206.12.95.102/solar_capacity_factor?year=2021&key={api_key}&year={year}', index_col=0)
    solar.index = solar.index-1
    solar.index = pd.to_datetime(year, format='%Y') + pd.to_timedelta(solar.index, unit='h')

    solar = solar.T
    solar.index = solar.index.astype(int)
    solar = pd.merge(solar, grid_cell, left_index=True, right_on='grid_cell')
    solar['variable'] = 'VRE Capacity Factor|Solar|' + solar['grid_cell'].astype(str) + '|' + solar['latitude'].astype(str) + '_' + solar['longitude'].astype(str)
    solar = solar.drop(columns=['latitude', 'longitude','grid_cell'])
    solar.rename(columns={'balancing_area': 'region'}, inplace=True)

    solar_melted = solar.melt(id_vars=['variable', 'region'], var_name='time', value_name='value')

    all_cf = pd.concat([wind_melted, solar_melted], ignore_index=True)
    return all_cf

if __name__ == '__main__':
    api_key = ''
    # df = get_hydro_data(api_key, 'AB', 2021)
    df2 = get_wind_solar_data(api_key, 2021)
