import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import pandas as pd

from datetime import datetime, timedelta

import xarray as xr

import seaborn as sns

import matplotlib.pyplot as plt

from plotly import tools
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import numpy as np

import fsspec
import requests

app = dash.Dash(__name__)


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



def load_data(location, years):
	dataframes_list = []

	for year in years:
		#filename = f"http://hpgregorio.net/nc_ondas/ONDAS_{location}_{year}.nc"
		filename = f"ONDAS_{location}_{year}.nc"
		file = fsspec.open(filename)
		#dataset = xr.open_dataset(file.open())
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

		dataframes_list.append(df)
		dataset.close()

	return pd.concat(dataframes_list, ignore_index=True)




# Função para plotar distribuição mensal de altura
def plot_monthly_stats(df, selected_years, bins, labels, parametro, nome_parametro, bin_color_map):
	# Criando uma coluna no dataframe para representar o intervalo de altura
	if parametro == 'CardinalDirection':
		df['Range'] = pd.Categorical(df[parametro], categories=bins, ordered=True)
	else:
		df['Range'] = pd.cut(df[parametro], bins=bins, labels=labels, right=False)
	
	# Calculando a distribuição de altura das ondas em cada intervalo por mês
	height_distribution = df.groupby([df['Datetime'].dt.month, 'Range'])[parametro].count().unstack()

	# Calculando a porcentagem da distribuição
	height_distribution_percentage = height_distribution.div(height_distribution.sum(axis=1), axis=0) * 100

	# Obtendo os nomes dos meses
	month_names = ['Jan', 'Fev', 'Mar' , 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
	
	title_years = f"{selected_years[0]} a {selected_years[-1]}"

	# Criando o gráfico de barras empilhadas com Plotly
	traces = []
	for col in height_distribution_percentage.columns:
		trace = go.Bar(
			x=month_names,
			y=height_distribution_percentage[col],
			name=f'{col}',
			marker=dict(color=bin_color_map[col])  
		)
		traces.append(trace)

	layout = go.Layout(
		title=f'{nome_parametro} - {title_years}',
		yaxis=dict(title='Frequência de ocorrência (%)', range=[0, 100]),
		legend=dict(title='', font=dict(size=12)),
		barmode='stack',
		height=400,
		width=600,
		plot_bgcolor='white',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001
	)

	fig = go.Figure(data=traces, layout=layout)

	return fig


def plot_annual_stats(df, selected_years, mes, bins, labels, parametro, nome_parametro, bin_color_map):
	
	month_data = df[df['Datetime'].dt.month == mes]

	if parametro == 'CardinalDirection':
		month_data['Range'] = pd.Categorical(month_data[parametro], categories=bins, ordered=True)
	else:
		month_data['Range'] = pd.cut(month_data[parametro], bins=bins, labels=labels, right=False)

	month_height_distribution = month_data.groupby([month_data['Datetime'].dt.year, 'Range'])[parametro].count().unstack()
	month_height_distribution_percentage = month_height_distribution.div(month_height_distribution.sum(axis=1), axis=0) * 100

	years = list(selected_years)  # Converter para lista
	
	month_names = ['Janeiro', 'Fevereiro', 'Março' , 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
	
	title_month = f"{month_names[mes-1]}"

	traces = []
	for col in month_height_distribution_percentage.columns:
		trace = go.Bar(
			x=years,
			y=month_height_distribution_percentage[col],
			name=f'{col}',
			marker=dict(color=bin_color_map[col])  
		)
		traces.append(trace)

	layout = go.Layout(
		title=f'{nome_parametro} - {title_month}',
		yaxis=dict(title='Frequência de ocorrência (%)', range=[0, 100]),
		legend=dict(title='', font=dict(size=12)),
		barmode='stack',
		height=400,
		width=600,
		plot_bgcolor='white',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001
	)
	
	#step_size = 1
	years_ticks = list(selected_years)
	layout.update(xaxis=dict(tickvals=years_ticks, ticktext=years_ticks, tickfont=dict(size=8)))

	fig = go.Figure(data=traces, layout=layout)

	return fig

































# ...

# Layout da aplicação
app.layout = html.Div([
#	html.H1("Ondas"),
	html.Label("Selecione o local:"),
	dcc.Dropdown(
		id='location-dropdown',
		options=[
			{'label': 'COSTA RICA (NORTE - 10.1N 85.9W)', 'value': 'CRICANORTE'},
			{'label': 'COSTA RICA (SUL - 8.1N 83.2W)', 'value': 'CRICASUL'},
			{'label': 'EL SALVADOR (EL TUNCO - 13N 89.4W)', 'value': 'ELSALVADOR'},
			{'label': 'MARROCOS (SIDI KAOKI - 30.55N 9.9W)', 'value': 'MARROCOSKAOKI'},
			{'label': 'MARROCOS (TAGHAZOUT - 30.4N 9.8W)', 'value': 'MARROCOSTAGHAZOUT'},
			{'label': 'MARROCOS (MIRLEFT - 29.5N 10.2W)', 'value': 'MARROCOSMIRLEFT'},
			{'label': 'SÃO SEBASTIÃO (24.4S 45.5W)', 'value': 'SAOSEBASTIAO'},
			{'label': 'PACASMAYO (7.4S 79.8W)', 'value': 'PACASMAYO'}
			# Adicione mais opções de local conforme necessário
		],
		value='PACASMAYO'
	),
	
	html.Br(), 

	html.Label("Selecione os anos:"),
	dcc.RangeSlider(
		id='year-slider',
		min=1993,
		max=2023,
		step=1,
		marks={i: str(i) for i in range(1993, 2024)},
		value=[1993, 2023]
	),
	

	html.Br(), 


	# Envolver os gráficos em uma linha
	html.Div([
		dcc.Graph(id='monthly-stats-plot-alt', style={'display': 'inline-block', 'width': '32%'}),

		dcc.Graph(id='monthly-stats-plot-dir', style={'display': 'inline-block', 'width': '32%'}),
		
		dcc.Graph(id='monthly-stats-plot-per', style={'display': 'inline-block', 'width': '32%'}),
	]),
	
	
	html.Label("Selecione o mês:"),
	dcc.Dropdown(
		id='month-dropdown',
		options=[
			{'label': month, 'value': i+1} for i, month in enumerate(['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
		],
		value=1
	),

	# Gráficos anuais
	html.Div([
		dcc.Graph(id='annual-stats-plot-alt', style={'display': 'inline-block', 'width': '32%'}),

		dcc.Graph(id='annual-stats-plot-dir', style={'display': 'inline-block', 'width': '32%'}),
		
		dcc.Graph(id='annual-stats-plot-per', style={'display': 'inline-block', 'width': '32%'}),
	]),
	
	
])



# Callbacks para atualizar os gráficos
@app.callback(
	[Output('monthly-stats-plot-alt', 'figure'),
	 Output('monthly-stats-plot-dir', 'figure'),
	 Output('monthly-stats-plot-per', 'figure'),
	 #Output('matrix', 'figure'),
	 Output('annual-stats-plot-alt', 'figure'),
	 Output('annual-stats-plot-dir', 'figure'),
	 Output('annual-stats-plot-per', 'figure')],
	[Input('location-dropdown', 'value'),
	 Input('year-slider', 'value'),
	 Input('month-dropdown', 'value')]
)

def update_plots(selected_location, selected_years, selected_month):
	
	# Carregar dados
	df = load_data(selected_location, list(range(selected_years[0], selected_years[1] + 1)))


	bins = [0, 1.0, 1.5, 2.0, 2.5, float('inf')]
	labels = ['< 1,0', '1,0-1,5', '1,5-2,0', '2,0-2,5', '> 2,5']
	parametro = 'VHM0'
	nome_parametro = 'Altura significativa (m)'
	
	#bin_color_map = {
	#'< 1,0': 'rgb(217,195,26)',
	#'1,0-1,5': 'rgb(162,146,73)',
	#'1,5-2,0': 'rgb(84,85,86)',
	#'2,0-2,5': 'rgb(32,44,78)',
	#'> 2,5': 'rgb(0,9,54)'}
	
	bin_color_map = {
	'< 1,0': 'rgb(207,159,0)',
	'1,0-1,5': 'rgb(190,96,0)',
	'1,5-2,0': 'rgb(165,30,0)',
	'2,0-2,5': 'rgb(129,0,111)',
	'> 2,5': 'rgb(44,0,98)'}

	fig1 = plot_monthly_stats(df, list(range(selected_years[0], selected_years[1] + 1)), bins, labels, parametro, nome_parametro,bin_color_map)
	fig4 = plot_annual_stats(df, list(range(selected_years[0], selected_years[1] + 1)), selected_month, bins, labels, parametro, nome_parametro,bin_color_map)


	bins = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
	labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
	parametro = 'CardinalDirection'
	nome_parametro = 'Direção de onda'
	
	bin_color_map = {
	'N': 'rgb(24,0,33)',
	'NE': 'rgb(60,15,111)',
	'E': 'rgb(67,78,150)',
	'SE': 'rgb(102,138,162)',
	'S': 'rgb(181,180,186)',
	'SW': 'rgb(171,135,111)',
	'W': 'rgb(148,64,54)',
	'NW': 'rgb(109,15,51)'}
	
	
	fig2 = plot_monthly_stats(df, list(range(selected_years[0], selected_years[1] + 1)), bins, labels, parametro, nome_parametro,bin_color_map)
	fig5 = plot_annual_stats(df,list(range(selected_years[0], selected_years[1] + 1)), selected_month, bins, labels, parametro, nome_parametro,bin_color_map)


	bins = [0, 8, 10, 12, 14, 16, float('inf')]
	labels = ['< 8', '8-10', '10-12', '12-14', '14-16', '> 16']
	parametro = 'VTPK'
	nome_parametro = 'Período de pico (s)'
	
	bin_color_map = {
	'< 8': 'rgb(255,255,229)',
	'8-10': 'rgb(243,250,182)',
	'10-12': 'rgb(203,234,156)',
	'12-14': 'rgb(159,215,136)',
	'14-16': 'rgb(66,171,93)',
	'> 16': 'rgb(0,69,41)'}
	
	fig3 = plot_monthly_stats(df, list(range(selected_years[0], selected_years[1] + 1)), bins, labels, parametro, nome_parametro,bin_color_map)
	fig6 = plot_annual_stats(df, list(range(selected_years[0], selected_years[1] + 1)), selected_month, bins, labels, parametro, nome_parametro,bin_color_map)
	
	
	#fig4 = analyze_and_visualize_data_dash(df)
	
	#fig5 = plot_annual_stats(df, selected_month, bins, labels, parametro, nome_parametro)

	return fig1, fig2, fig3, fig4, fig5, fig6

# ...

if __name__ == '__main__':
	app.run_server(debug=True)
