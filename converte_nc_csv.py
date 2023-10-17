import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
import numpy as np

# Definir a função convert_to_cardinal, se ainda não estiver definida
def convert_to_cardinal(direction_numeric):
	cardinal_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
	dir_grid = np.arange(-22.5, 360, 45)
	dir_grid[0] = 360 - 22.5

	index = np.searchsorted(dir_grid, direction_numeric, side='right') - 1

	# Corrigir para valores próximos a 360
	if direction_numeric > 337.5 or direction_numeric < 0.0:
		index = 0

	index = np.clip(index, 0, len(cardinal_directions) - 1)

	return cardinal_directions[index]

# Definir a função convert_nc_to_csv
def convert_nc_to_csv(location, years):
    dataframes_list = []

    for year in years:
        filename_nc = f"ONDAS_{location}_{year}.nc"
        dataset = xr.open_dataset(filename_nc)

        start_date = datetime(year, 1, 1, 0, 0)
        time_steps = dataset.dims['time']
        time_array = [start_date + timedelta(hours=3 * i) for i in range(time_steps)]

        df = pd.DataFrame({
            'Datetime': time_array,
            'VHM0': dataset['VHM0'].squeeze().values,
            'VMDR': dataset['VMDR'].squeeze().values,
            'VTPK': dataset['VTPK'].squeeze().values
        })

        # Converter direções numéricas para direções cardinais
        df['CardinalDirection'] = df['VMDR'].apply(convert_to_cardinal)

        csv_filename = f"ONDAS_{location}_{year}.csv"
        df.to_csv(csv_filename, index=False)

        dataframes_list.append(df)
        dataset.close()

    return pd.concat(dataframes_list, ignore_index=True)

# Localizações e anos desejados
locations = [
    'ELMERS'
]

years = list(range(1993, 2024))

# Loop para converter os arquivos para CSV
for location in locations:
    convert_nc_to_csv(location, years)
