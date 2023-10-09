
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import seaborn as sns


# Função para converter direções numéricas em direções cardinais
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



def load_data(location, years, selected_directions, period_cutoff):
	dataframes_list = []

	for year in years:
		filename = f"ONDAS_{location}_{year}.nc"
		dataset = xr.open_dataset(filename)
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

		# Filtrar pelas direções selecionadas (coloca altura = 0)
		df['VHM0'] = np.where(df['CardinalDirection'].isin(selected_directions), df['VHM0'], 0)

		# Filtrar pelo período de corte  (coloca altura = 0)
		df['VHM0'] = np.where(df['VTPK'] >= period_cutoff, df['VHM0'], 0)
		
		dataframes_list.append(df)
		dataset.close()

	return pd.concat(dataframes_list, ignore_index=True)


def analyze_and_visualize_data(df):
	# Definindo os intervalos para análise
	altura_bins = [0, 1.0, 1.5, 2.0, 2.5, float('inf')]
	direcao_bins = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
	periodo_bins = [0, 8, 10, 12, 14, 16, float('inf')]

	# Criando os intervalos formatados
	altura_labels = ['< 1.0', '1.0-1.5', '1.5-2.0', '2.0-2.5', '> 2.5']
	periodo_labels = ['< 8', '8-10', '10-12', '12-14', '14-16', '> 16']

	# Criando as matrizes
	matrices = {}
	for analysis_type in ['Altura x Direção', 'Período x Direção', 'Altura x Período']:
		matrices[analysis_type] = {}
		for month in range(1, 13):
			month_df = df[df['Datetime'].dt.month == month]

			if analysis_type == 'Altura x Direção':
				matrix = pd.crosstab(pd.cut(month_df['VHM0'], bins=altura_bins, labels=altura_labels, right=False),
									 pd.Categorical(month_df['CardinalDirection'], categories=direcao_bins),
									 margins=False, dropna=False)
			elif analysis_type == 'Período x Direção':
				matrix = pd.crosstab(pd.cut(month_df['VTPK'], bins=periodo_bins, labels=periodo_labels, right=False),
									 pd.Categorical(month_df['CardinalDirection'], categories=direcao_bins),
									 margins=False, dropna=False)
			elif analysis_type == 'Altura x Período':
				matrix = pd.crosstab(pd.cut(month_df['VHM0'], bins=altura_bins, labels=altura_labels, right=False),
									 pd.cut(month_df['VTPK'], bins=periodo_bins, labels=periodo_labels, right=False),
									 margins=False, dropna=False)
			matrix_percentage = matrix / np.sum(np.sum(matrix)) * 100
			matrices[analysis_type][month] = matrix_percentage

	# Visualizando as matrizes
	
	month_names = ['Jan', 'Fev', 'Mar' , 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
	fig, axes = plt.subplots(12, 3, figsize=(15, 30),gridspec_kw={'hspace': 0.05})

	for row, month in enumerate(range(1, 13)):
		# Adicionando o mês à lateral esquerda da linha
		axes[row, 0].text(-2, 0.5, month_names[month-1], fontsize=12, va='center', ha='center')

		for col, analysis_type in enumerate(['Altura x Direção', 'Período x Direção', 'Altura x Período']):
			matrix_percentage = matrices[analysis_type][month]

			if analysis_type == 'Altura x Direção': 
				sns.heatmap(matrix_percentage, annot=True, fmt=".0f", cmap="RdPu", ax=axes[row, col], cbar=False)
			
			if analysis_type == 'Período x Direção': 
				sns.heatmap(matrix_percentage, annot=True, fmt=".0f", cmap="YlGn", ax=axes[row, col], cbar=False)

			if analysis_type == 'Altura x Período': 
				sns.heatmap(matrix_percentage, annot=True, fmt=".0f", cmap="PuBu", ax=axes[row, col], cbar=False)			
			axes[row, col].set_ylabel('');
			axes[row, col].set_xlabel('');
			
			if row == 0:
				axes[row, col].set_title(analysis_type)

			if row != 11:
				axes[row, col].set_xticklabels([])
			if row == 11:
				axes[row, col].set_xticklabels(axes[row, col].get_xticklabels(), rotation=45, ha='right')

	plt.tight_layout()
	plt.show()
	
	
location = 'SAOSEBASTIAO'
years = range(1993,2024);  # Substitua pelos anos desejados
selected_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
period_cutoff = 0  # Substitua pelo período desejado
df = load_data(location, years, selected_directions, period_cutoff)

analyze_and_visualize_data(df)