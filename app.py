import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
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
import os


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.SPACELAB,dbc.icons.FONT_AWESOME])
server = app.server

def load_data(location, years):
    dataframes_list = []

    for year in years:
        filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/csv/ONDAS_{location}_{year}.csv"
        #filename_csv = f"csv/ONDAS_{location}_{year}.csv"
		
        df = pd.read_csv(filename_csv)
		
        df['Datetime'] = pd.to_datetime(df['Datetime'])

        dataframes_list.append(df)

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
	month_names = ['Jan', 'Feb', 'Mar' , 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

	title_years = f"{selected_years[0]} to {selected_years[-1]}"

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
		yaxis=dict(title='Occurency (%)', range=[0, 100]),
		legend=dict(title='', font=dict(size=10)),
		barmode='stack',
		height=450,
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

	month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

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
		yaxis=dict(title='Occurency (%)', range=[0, 100]),
		legend=dict(title='', font=dict(size=10)),
		barmode='stack',
		height=450,
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












def plot_custom_conditions_frequency(df, conditions, selected_years):
	# Criando uma coluna para verificar se cada linha atende às condições
	df['ConditionMet'] = False

	for condition_set in conditions:
		# Verificando se há pelo menos uma condição no conjunto
		if any(condition_set.values()):
			condition_met_set = (df['VHM0'] >= condition_set['altura']) & (df['VTPK'] >= condition_set['periodo'])
			if condition_set['direcao'] is not None:
				if condition_set['direcao']:
					condition_met_set &= (df['CardinalDirection'] == condition_set['direcao'])

			# Considerando "E" dentro do conjunto de condições
			df['ConditionMet'] |= condition_met_set

	# Agrupando por mês e contando o número de ocorrências onde as condições foram atendidas
	monthly_condition_counts = df.groupby(df['Datetime'].dt.month)['ConditionMet'].sum()

	# Calculando a porcentagem de ocorrências atendendo às condições para cada mês
	monthly_condition_percentage = (monthly_condition_counts / df.groupby(df['Datetime'].dt.month)['ConditionMet'].count()) * 100

	month_names = ['Jan', 'Feb', 'Mar' , 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	title_years = f"{selected_years[0]} to {selected_years[-1]}"
	# Criando o gráfico de barras
	trace = go.Bar(
		x=month_names,
		y=monthly_condition_percentage,
		marker=dict(color='rgb(67, 78, 150)')
	)

	layout = go.Layout(
		title=f'Occurency according with the conditions - {title_years}',
		yaxis=dict(title='Occurency (%)', range=[0, 100]),
		plot_bgcolor='white',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001,
		height=450,
		width=600,
	)

	fig = go.Figure(data=[trace], layout=layout)
	return fig
























app.layout = dbc.Container([

	html.Label("Location:"),
	dcc.Dropdown(
		id='location-dropdown',
		options=[
			{'label': 'BRAZIL (JERICOACOARA - 2.77S 40.52W)', 'value': 'JERICOACOARA'},
			{'label': 'BRAZIL (SÃO SEBASTIÃO - 24.4S 45.5W)', 'value': 'SAOSEBASTIAO'},
			{'label': 'BRAZIL (SANTOS/GUARUJÁ - 24.15S 46.2W)', 'value': 'SANTOSGUARUJA'},			
			{'label': 'COSTA RICA (GUANACASTE - 10.1N 85.9W)', 'value': 'CRICANORTE'},
			{'label': 'COSTA RICA (PENINSULA OSA - 8.1N 83.2W)', 'value': 'CRICASUL'},
			{'label': 'EL SALVADOR (EL TUNCO - 13N 89.4W)', 'value': 'ELSALVADOR'},
			{'label': 'MARROCOS (SIDI KAOKI - 30.55N 9.9W)', 'value': 'MARROCOSKAOKI'},
			{'label': 'MARROCOS (TAGHAZOUT - 30.4N 9.8W)', 'value': 'MARROCOSTAGHAZOUT'},
			{'label': 'MARROCOS (MIRLEFT - 29.5N 10.2W)', 'value': 'MARROCOSMIRLEFT'},
			{'label': 'PERU (PACASMAYO - 7.4S 79.8W)', 'value': 'PACASMAYO'}
			# Adicione mais opções de local conforme necessário
		],
		value='SAOSEBASTIAO'
	),

	html.Br(),

	html.Label("Years selection:"),
	dcc.RangeSlider(
		id='year-slider',
		min=1993,
		max=2023,
		step=1,
		marks={i: str(i) for i in range(1993, 2024)},
		value=[1993, 2023]
	),


	dbc.Tabs([
		dbc.Tab(label="Waves", tab_id="waves"),
		dbc.Tab(label="Wind", tab_id="wind"),
		dbc.Tab(label="Othes", tab_id="others"),
            ],
            id="tabs",
            active_tab="waves",
            style={'width': '100%', 'border': 'none'}
        ),
        html.Div(id="tab-content", className="p-4"),
    ]
)


app.layout = dbc.Container([
    html.Label("Location:"),
    dcc.Dropdown(
        id='location-dropdown',
        options=[
			{'label': 'BRAZIL (JERICOACOARA - 2.77S 40.52W)', 'value': 'JERICOACOARA'},
			{'label': 'BRAZIL (SÃO SEBASTIÃO - 24.4S 45.5W)', 'value': 'SAOSEBASTIAO'},
			{'label': 'BRAZIL (SANTOS/GUARUJÁ - 24.15S 46.2W)', 'value': 'SANTOSGUARUJA'},			
			{'label': 'COSTA RICA (GUANACASTE - 10.1N 85.9W)', 'value': 'CRICANORTE'},
			{'label': 'COSTA RICA (PENINSULA OSA - 8.1N 83.2W)', 'value': 'CRICASUL'},
			{'label': 'EL SALVADOR (EL TUNCO - 13N 89.4W)', 'value': 'ELSALVADOR'},
			{'label': 'MARROCOS (SIDI KAOKI - 30.55N 9.9W)', 'value': 'MARROCOSKAOKI'},
			{'label': 'MARROCOS (TAGHAZOUT - 30.4N 9.8W)', 'value': 'MARROCOSTAGHAZOUT'},
			{'label': 'MARROCOS (MIRLEFT - 29.5N 10.2W)', 'value': 'MARROCOSMIRLEFT'},
			{'label': 'PERU (PACASMAYO - 7.4S 79.8W)', 'value': 'PACASMAYO'}
			# Adicione mais opções de local conforme necessário
		],
        value='SAOSEBASTIAO'
    ),

    html.Br(),

    html.Label("Years selection:"),
    dcc.RangeSlider(
        id='year-slider',
        min=1993,
        max=2023,
        step=1,
        marks={i: str(i) for i in range(1993, 2024)},
        value=[1993, 2023]
    ),

    dbc.Tabs([
        dbc.Tab(label="Waves", tab_id="waves"),
        dbc.Tab(label="Wind", tab_id="wind"),
        dbc.Tab(label="Others", tab_id="others"),
    ],
        id="tabs",
        active_tab="waves",
    ),

    html.Div(id="tab-content", className="p-4"),

    dbc.Tab(label="Waves", tab_id="waves"),
    dbc.Tab(label="Wind", tab_id="wind"),
    dbc.Tab(label="Others", tab_id="others"),
	
	
    html.Div([
        dcc.Graph(id='monthly-stats-plot-alt', style={'width': '100%'}),
        dcc.Graph(id='monthly-stats-plot-dir', style={'width': '100%'}),
        dcc.Graph(id='monthly-stats-plot-per', style={'width': '100%'}),
    ], id="waves-content"),
	
	
	





	# Layout para as condições
	html.Div([
		html.Label("Condition 1:"),
		dcc.Input(id='altura1', type='number', placeholder='Height'),
		dcc.Input(id='periodo1', type='number', placeholder='Period'),
		dcc.Input(id='direcao1', type='text', placeholder='Direction (none = ALL)'),
	], style={'width': '100%'}),
	html.Div([
		html.Label("OR Condition 2:"),
		dcc.Input(id='altura2', type='number', placeholder='Height'),
		dcc.Input(id='periodo2', type='number', placeholder='Period'),
		dcc.Input(id='direcao2', type='text', placeholder='Direction (none = ALL)'),
	], style={'width': '100%'}),
    html.Div([
		html.Label("OR Condition 3:"),
		dcc.Input(id='altura3', type='number', placeholder='Height'),
		dcc.Input(id='periodo3', type='number', placeholder='Period'),
		dcc.Input(id='direcao3', type='text', placeholder='Direction (none = ALL)'),
	], style={'width': '100%'}),
	


	dcc.Graph(id='custom-conditions-plot', style={'width': '100%'}),
	

	html.Br(),

	# Dropdown "Selecione o mês"
	html.Div([
		html.Div([
			html.Label("Select the month:"),
			dcc.Dropdown(
				id='month-dropdown',
				options=[
					{'label': month, 'value': i+1} for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
				],
				value=1,
				style={'width': '100%', 'display': 'inline-block'}
			),
		]),
	]),

	# Gráficos anuais
	html.Div([
		dcc.Graph(id='annual-stats-plot-alt', style={'width': '100%'}),

		dcc.Graph(id='annual-stats-plot-dir', style={'width': '100%'}),

		dcc.Graph(id='annual-stats-plot-per', style={'width': '100%'}),
	], id="waves-annual-plot"),


])



# Callbacks para atualizar os gráficos
@app.callback(
	[Output('monthly-stats-plot-alt', 'figure'),
	 Output('monthly-stats-plot-dir', 'figure'),
	 Output('monthly-stats-plot-per', 'figure'),
	 Output('custom-conditions-plot', 'figure'),
	 Output('annual-stats-plot-alt', 'figure'),
	 Output('annual-stats-plot-dir', 'figure'),
	 Output('annual-stats-plot-per', 'figure')],
	[Input('location-dropdown', 'value'),
	 Input('year-slider', 'value'),
	 Input('month-dropdown', 'value'),
	 Input('altura1', 'value'),
	 Input('periodo1', 'value'),
	 Input('direcao1', 'value'),
	 Input('altura2', 'value'),
	 Input('periodo2', 'value'),
	 Input('direcao2', 'value'),
	 Input('altura3', 'value'),
	 Input('periodo3', 'value'),
	 Input('direcao3', 'value')],
	 [State("tabs", "active_tab")] 
)


def update_plots(selected_location, selected_years, selected_month,altura1, periodo1, direcao1,altura2, periodo2, direcao2,altura3, periodo3, direcao3, active_tab):

	# Carregar dados
	df = load_data(selected_location, list(range(selected_years[0], selected_years[1] + 1)))

	if active_tab == "waves":
		bins = [0, 1.0, 1.5, 2.0, 2.5, float('inf')]
		labels = ['< 1,0', '1,0-1,5', '1,5-2,0', '2,0-2,5', '> 2,5']
		parametro = 'VHM0'
		nome_parametro = 'Significant Wave Height (m)'

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
		nome_parametro = 'Wave direction'

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
		nome_parametro = 'Peak wave period (s)'

		bin_color_map = {
		'< 8': 'rgb(255,255,229)',
		'8-10': 'rgb(243,250,182)',
		'10-12': 'rgb(203,234,156)',
		'12-14': 'rgb(159,215,136)',
		'14-16': 'rgb(66,171,93)',
		'> 16': 'rgb(0,69,41)'}

		fig3 = plot_monthly_stats(df, list(range(selected_years[0], selected_years[1] + 1)), bins, labels, parametro, nome_parametro,bin_color_map)
		fig6 = plot_annual_stats(df, list(range(selected_years[0], selected_years[1] + 1)), selected_month, bins, labels, parametro, nome_parametro,bin_color_map)


		
		# Condições do usuário
		conditions = [{'altura': altura1, 'periodo': periodo1, 'direcao': direcao1},
		{'altura': altura2, 'periodo': periodo2, 'direcao': direcao2},
		{'altura': altura3, 'periodo': periodo3, 'direcao': direcao3}]
		
		fig_custom_conditions = plot_custom_conditions_frequency(df, conditions, list(range(selected_years[0], selected_years[1] + 1)))
		

		return fig1, fig2, fig3, fig_custom_conditions, fig4, fig5, fig6

# ...

if __name__ == '__main__':
	app.run_server(debug=True)
