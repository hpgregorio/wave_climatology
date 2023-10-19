import pandas as pd

# Provided lists
tit = {'JERICOACOARA': 'Jericoacoara/CE (Brazil)',
       'SAOSEBASTIAO': 'São Sebastião/SP (Brazil)',
       'CRICANORTE': 'Guanacaste (Costa Rica)',
       'CRICASUL': 'Peninsula Osa (Costa Rica)',
       'ELSALVADOR': 'El Tunco (El Salvador)',
       'MARROCOSKAOKI': 'Sidi Kaoki (Morocco)',
       'MARROCOSTAGHAZOUT': 'Taghazout (Morocco)',
       'MARROCOSMIRLEFT': 'Mirleft (Morocco)',
       'PACASMAYO': 'Pacasmayo (Peru)',
       'ELMERS': 'Elmers Island/LA (USA)'}

WIND_TYPES = {
    'JERICOACOARA': {
        'onshore': ['N'],
        'offshore': ['S'],
        'side': ['W', 'E'],
        'side_onshore': ['NE', 'NW'],
        'side_offshore': ['SE', 'SW'],
    },
    'SAOSEBASTIAO': {
        'onshore': ['SW', 'S'],
        'offshore': ['NE', 'N'],
        'side': ['W', 'E'],
        'side_onshore': ['SE'],
        'side_offshore': ['NW'],
    },
    'CRICANORTE': {
        'onshore': ['W', 'SW'],
        'offshore': ['E', 'NE'],
        'side': ['NW', 'SE'],
        'side_onshore': ['S'],
        'side_offshore': ['N'],
    },
    'CRICASUL': {
        'onshore': ['E'],
        'offshore': ['W'],
        'side': ['N', 'S'],
        'side_onshore': ['NE', 'SE'],
        'side_offshore': ['NW', 'SW'],
    },
    'ELSALVADOR': {
        'onshore': ['S'],
        'offshore': ['N'],
        'side': ['W', 'E'],
        'side_onshore': ['SW', 'SE'],
        'side_offshore': ['NW', 'NE'],
    },
    'MARROCOSKAOKI': {
        'onshore': ['W'],
        'offshore': ['E'],
        'side': ['N', 'S'],
        'side_onshore': ['NW', 'SW'],
        'side_offshore': ['NE', 'SE'],
    },
    'MARROCOSTAGHAZOUT': {
        'onshore': ['W'],
        'offshore': ['E'],
        'side': ['N', 'S'],
        'side_onshore': ['NW', 'SW'],
        'side_offshore': ['NE', 'SE'],
    },
    'MARROCOSMIRLEFT': {
        'onshore': ['NW'],
        'offshore': ['SE'],
        'side': ['NE', 'SW'],
        'side_onshore': ['N', 'W'],
        'side_offshore': ['S', 'E'],
    },
    'PACASMAYO': {
        'onshore': ['NW', 'W'],
        'offshore': ['SE', 'E'],
        'side': ['SW', 'NE'],
        'side_onshore': ['N'],
        'side_offshore': ['S'],
    },
    'ELMERS': {
        'onshore': ['SE'],
        'offshore': ['NW'],
        'side': ['NE', 'SW'],
        'side_onshore': ['E', 'S'],
        'side_offshore': ['N', 'W'],
    },
}

TIME_ZONES = {
    'JERICOACOARA': -3,
    'SAOSEBASTIAO': -3,
    'CRICANORTE': -6,
    'CRICASUL': -6,
    'ELSALVADOR': -6,
    'MARROCOSKAOKI': +1,
    'MARROCOSTAGHAZOUT': +1,
    'MARROCOSMIRLEFT': +1,
    'PACASMAYO': -5,
    'ELMERS': -5,
}

# Create a DataFrame combining the information
df_combined = pd.DataFrame(list(tit.items()), columns=['location', 'title'])
df_combined = df_combined.join(pd.DataFrame(WIND_TYPES).T, on='location')
df_combined['time_zone'] = df_combined['location'].map(TIME_ZONES)

# Write the combined information to a CSV file
df_combined.to_csv('combined_information.csv', index=False)

# Display the combined DataFrame
print(df_combined)