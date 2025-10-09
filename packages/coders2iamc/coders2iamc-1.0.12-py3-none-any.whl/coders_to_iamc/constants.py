CODERS = 'https://api.sesit.ca/'

gen_type_copper_mapping = {
    'biogas': 'biomass',
    'biomass': 'biomass',
    'Biomass': 'biomass',
    'biomass_CG': 'biomass',

    'coal': 'coal',
    'coal_CCS': 'coalCCS',

    'diesel_CT': 'diesel',
    'diesel_ST': 'diesel',
    
    'gasoline_CT': 'diesel',

    'geothermal': 'geothermal',

    'h2blue_CT': 'h2blue_CT',
    'h2green_CT': 'h2green_CT',

    'hydro_daily': 'hydro_daily',
    'hydro_monthly': 'hydro_monthly',
    'hydro_run': 'hydro_run',

    'MSW': 'biomass',

    'NG_CC': 'NG_CC',
    'NG_CCS': 'NG_CCS',
    'NG_CG': 'NG_CG',
    'NG_SC': 'NG_SC',

    'nuclear': 'nuclear',
    'nuclear_SMR': 'nuclear_SMR',

    'oil_CT': 'diesel',
    'oil_ST': 'diesel',

    'solar_PV': 'solar',
    'solar_recon': 'solar_recon',

    'storage_air': 'storage_LI',
    'storage_flywheel': 'storage_LI',
    'storage_lithium': 'storage_LI',
    'storage_pump': 'storage_PH',
    'storage_solid': 'storage_LI',

    'wind_ofs': 'wind_ofs',
    'wind_ons': 'wind_ons',
    'wind_recon': 'wind_recon',
}