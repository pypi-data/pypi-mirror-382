from urllib.request import urlopen
import pandas as pd
import json

mappings = {
    'average_fuel_price_CAD_per_MMBtu': 'Cost|Fuel|',
    'variable_om_costs': 'Cost|Variable O&M|',
}

def get_data(api_key: str):
    with urlopen(f"https://api.sesit.ca/generation_generic?key={api_key}") as response:
        response_content = response.read()
        json_response = json.loads(response_content)
        modeled_attributes = pd.json_normalize(json_response)

    modeled_attributes = modeled_attributes[
        ['variable_om_costs', 'average_fuel_price_CAD_per_MMBtu', 'gen_type_copper']]
    modeled_attributes['average_fuel_price_CAD_per_MMBtu'] = modeled_attributes[
                                                                 'average_fuel_price_CAD_per_MMBtu'].astype(float)
    melted = modeled_attributes.melt(id_vars=['gen_type_copper'], var_name='variable', value_name='value')

    melted['variable'] = melted['variable'].map(mappings)
    melted['variable'] = melted['variable'] + melted['gen_type_copper'].astype(str)
    melted = melted.drop(columns=['gen_type_copper'])

    return melted

if __name__ == '__main__':
    api_key = ''
    df = get_data(api_key)
    print(df)