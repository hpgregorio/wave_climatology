import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd

from plotly import tools
import plotly.graph_objs as go
from plotly.subplots import make_subplots

import numpy as np

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.SPACELAB,dbc.icons.FONT_AWESOME])
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

server = app.server


def load_data(location, years):
	dataframes_list = []

	for year in years:
		#filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/csv/ONDAS_{location}_{year}.csv"
		filename_csv = f"csv/ONDAS_{location}_{year}.csv"
		
		df = pd.read_csv(filename_csv)
		
		df['Datetime'] = pd.to_datetime(df['Datetime'])

		dataframes_list.append(df)

	return pd.concat(dataframes_list, ignore_index=True)
	
	
def load_data_wind(location, years):
	dataframes_list = []

	for year in years:
		#filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/ventos_csv/VENTOS_{location}_{year}.csv"
		filename_csv = f"ventos_csv/VENTOS_{location}_{year}.csv"
		
		df = pd.read_csv(filename_csv)
		
		df['Datetime'] = pd.to_datetime(df['Datetime'])

		dataframes_list.append(df)

	return pd.concat(dataframes_list, ignore_index=True)
	
	
def load_data_sst(location, years):
	dataframes_list = []

	for year in years:
		#filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/sst_csv/SST_{location}_{year}.csv"
		filename_csv = f"sst_csv/SST_{location}_{year}.csv"
		
		df = pd.read_csv(filename_csv)
		
		df['Datetime'] = pd.to_datetime(df['Datetime'])

		dataframes_list.append(df)

	return pd.concat(dataframes_list, ignore_index=True)
	
def plot_monthly_stats(df, selected_years, bins, labels, parametro, nome_parametro, bin_color_map, selected_hours=None):
	
	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		
		# Criando uma coluna no dataframe para representar o intervalo de altura
		if parametro == 'CardinalDirection' or parametro == 'WindType':
			df_selected_hours['Range'] = pd.Categorical(df_selected_hours[parametro], categories=bins, ordered=True)
		else:
			df_selected_hours['Range'] = pd.cut(df_selected_hours[parametro], bins=bins, labels=labels, right=False)

		# Calculando a distribuição de altura das ondas em cada intervalo por mês
		height_distribution = df_selected_hours.groupby([df_selected_hours['Datetime'].dt.month, 'Range'])[parametro].count().unstack()

	else:
		# Criando uma coluna no dataframe para representar o intervalo de altura
		if parametro == 'CardinalDirection' or parametro == 'WindType':
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
		height=350,
		width=400,
		plot_bgcolor='white',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001
	)

	fig = go.Figure(data=traces, layout=layout)

	return fig


def plot_annual_stats(df, selected_years, mes, bins, labels, parametro, nome_parametro, bin_color_map):

	month_data = df[df['Datetime'].dt.month == mes]

	if parametro == 'CardinalDirection' or parametro == 'WindType':
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
		height=350,
		width=400,
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
		title=f'Occurency according with the conditions<br>- {title_years}',
		yaxis=dict(title='Occurency (%)', range=[0, 100]),
		plot_bgcolor='white',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001,
		height=350,
		width=400,
	)

	fig = go.Figure(data=[trace], layout=layout)
	return fig

def plot_others(df, df_sst, selected_years, selected_hours=None):
	
	df['Month'] = df['Datetime'].dt.month
	df['Year'] = df['Datetime'].dt.year
	
	df_sst['Month'] = df_sst['Datetime'].dt.month
	df_sst['Year'] = df_sst['Datetime'].dt.year


	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		df_selected_hours['Month'] = df_selected_hours['Datetime'].dt.month
		df_selected_hours['Year'] = df_selected_hours['Datetime'].dt.year
		
		monthly_temp_avg = df_selected_hours.groupby('Month')['temp'].mean()
	else:
		monthly_temp_avg = df.groupby('Month')['temp'].mean()

	monthly_sst_avg = df_sst.groupby('Month')['sst'].mean()
	
	# Agrupe os dados por ano e mês, somando a coluna 'prec'
	monthly_prec_sum = df.groupby(['Year', 'Month'])['prec'].sum().reset_index()
	
	# Calcule a média mensal ao longo dos anos
	monthly_prec_avg = monthly_prec_sum.groupby('Month')['prec'].mean().reset_index()
	monthly_prec_avg = monthly_prec_avg*1000 #transformar para mm/mês
	
	month_names = ['Jan', 'Feb', 'Mar' , 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	fig = go.Figure()
	
	# Adicione barras para precipitação primeiro
	trace_prec = go.Bar(
		x=month_names,
		y=monthly_prec_avg['prec'],
		name='Precipitation',
		marker=dict(color='rgb(200, 200, 200)')
	)

	# Adicione os traços de linha
	trace_temp = go.Scatter(
		x=month_names,
		y=monthly_temp_avg,
		mode='lines+markers',
		name='Air Temp',
		line=dict(color='rgb(67, 78, 150)'),
		yaxis='y2'
	)

	trace_sst = go.Scatter(
		x=month_names,
		y=monthly_sst_avg,
		mode='lines+markers',
		name='Sea Temp',
		line=dict(color='rgb(220, 20, 60)'),
		yaxis='y2'
	)

	# Adicione os traços ao gráfico
	fig.add_trace(trace_prec)
	fig.add_trace(trace_temp)
	fig.add_trace(trace_sst)
	
	
	
	layout = go.Layout(
		title=f'Air Temp, Sea Temp and Prec<br>- {title_years}',
		yaxis=dict(title='Precipitation (mm/month)', range=[0, 200]),
		yaxis2=dict(
			title='Temperature (°C)',
			overlaying='y',
			side='right',
			range=[12, 32]
		),
		plot_bgcolor='white',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001,
		height=350,
		width=400,
		legend=dict(
			x=0.1,
			y=-0.15,
			orientation='h',
			bgcolor='rgba(255, 255, 255, 0.5)',
			traceorder='normal',  # Ordem padrão de exibição dos itens da legenda
			bordercolor='rgba(255, 255, 255, 0)',  # Cor da borda da legenda (transparente)
			borderwidth=0,  # Largura da borda da legenda
			xanchor='left',  # Ancoragem horizontal no centro
			yanchor='top'  # Ancoragem vertical no topo
		)
	)


	fig = go.Figure(data=[trace_temp,trace_sst,trace_prec], layout=layout)
	return fig

def plot_rose():

	fig = go.Figure()
	
	trace = [];
	trace = go.Barpolar(
		r=[4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5],
		theta=[0, 45, 90, 135, 180, 225, 270, 315],
		width=[40,40,40,40,40,40,40,40],
		marker_color=['rgb(24,0,33)','rgb(60,15,111)','rgb(67,78,150)','rgb(102,138,162)','rgb(181,180,186)','rgb(171,135,111)','rgb(148,64,54)','rgb(109,15,51)'],
		marker_line_color="black",
		marker_line_width=0.1
	)

	fig.add_trace(trace)
	
	fig.update_layout(
		showlegend = False,
		polar = dict(
			radialaxis = dict(
				tickvals=[0, 5],
				ticktext=["", ""],
				tickfont_size = 8,
				gridcolor = 'white',
				linecolor = 'rgb(67,78,150)'
				
			),
			angularaxis = dict(
				tickfont_size = 12,
				rotation = 90,
				direction = "clockwise",
				tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
				ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
				gridcolor = 'white',
				linecolor = 'black'
				
			),
			bgcolor='white'
		),
		height=100,
		width=100,
		margin=dict(l=20, r=20, t=20, b=20)

    )	

	return fig
	
def add_wind_type_column(df, onshore, side_onshore, offshore, side_offshore, side):
	conditions = [
		df['CardinalDirection'].isin(onshore),
		df['CardinalDirection'].isin(side_onshore),
		df['CardinalDirection'].isin(offshore),
		df['CardinalDirection'].isin(side_offshore),
		df['CardinalDirection'].isin(side)
	]

	choices = ['onshore', 'side-onshore', 'offshore', 'side-offshore', 'side']

	df['WindType'] = np.select(conditions, choices, default=None)

	return df		


def wind_type(selected_location):
	if selected_location == 'JERICOACOARA':
		onshore = ['N']
		offshore = ['S']
		side = ['W','E']
		side_onshore = ['NE','NW']
		side_offshore = ['SE','SW']


	if selected_location == 'SAOSEBASTIAO': 
		onshore = ['SW','S']
		offshore = ['NE','N']
		side = ['W','E']
		side_onshore = ['SE']
		side_offshore = ['NW']


	if selected_location == 'CRICANORTE':
		onshore = ['W','SW']
		offshore = ['E','NE']
		side = ['NW','SE']
		side_onshore = ['S']
		side_offshore = ['N']


	if selected_location == 'CRICASUL':
		onshore = ['E']
		offshore = ['W']
		side = ['N','S']
		side_onshore = ['NE','SE']
		side_offshore = ['NW','SW']


	if selected_location == 'ELSALVADOR':
		onshore = ['S']
		offshore = ['N']
		side = ['W','E']
		side_onshore = ['SW','SE']
		side_offshore = ['NW','NE']


	if selected_location == 'MARROCOSKAOKI':
		onshore = ['W']
		offshore = ['E']
		side = ['N','S']
		side_onshore = ['NW','SW']
		side_offshore = ['NE','SE']


	if selected_location == 'MARROCOSTAGHAZOUT':
		onshore = ['W']
		offshore = ['E']
		side = ['N','S']
		side_onshore = ['NW','SW']
		side_offshore = ['NE','SE']


	if selected_location == 'MARROCOSMIRLEFT':
		onshore = ['NW']
		offshore = ['SE']
		side = ['NE','SW']
		side_onshore = ['N','W']
		side_offshore = ['S','E']


	if selected_location == 'PACASMAYO':
		onshore = ['NW','W']
		offshore = ['SE','E']
		side = ['SW','NE']
		side_onshore = ['N']
		side_offshore = ['S']

	if selected_location == 'ELMERS':
		onshore = ['SE']
		offshore = ['NW']
		side = ['NE','SW']
		side_onshore = ['E','S']
		side_offshore = ['N','W']

	return onshore, offshore, side, side_onshore, side_offshore
	
	
# Função para converter os horários de acordo com o GMT específico
def converter_horarios_gmt(horarios, gmt):
	horarios_convertidos = [(hora + gmt) % 24 for hora in horarios]
	return horarios_convertidos

app.layout = dcc.Loading(
    id="loading-container",
    type='dot',
	fullscreen=True,
	color='rgba(0,0,0,0.2)',
	style={'backgroundColor': 'rgba(255,255,255,0.2)'},
    children=[

		dbc.Container([
		
			html.Label("Location:"),
			dcc.Dropdown(
				id='location-dropdown',
				options=[
					{'label': 'BRAZIL (JERICOACOARA - 2.77S 40.52W)', 'value': 'JERICOACOARA'},
					{'label': 'BRAZIL (SÃO SEBASTIÃO - 24.4S 45.5W)', 'value': 'SAOSEBASTIAO'},
					{'label': 'COSTA RICA (GUANACASTE - 10.1N 85.9W)', 'value': 'CRICANORTE'},
					{'label': 'COSTA RICA (PENINSULA OSA - 8.1N 83.2W)', 'value': 'CRICASUL'},
					{'label': 'EL SALVADOR (EL TUNCO - 13N 89.4W)', 'value': 'ELSALVADOR'},
					{'label': 'MARROCOS (SIDI KAOKI - 30.55N 9.9W)', 'value': 'MARROCOSKAOKI'},
					{'label': 'MARROCOS (TAGHAZOUT - 30.4N 9.8W)', 'value': 'MARROCOSTAGHAZOUT'},
					{'label': 'MARROCOS (MIRLEFT - 29.5N 10.2W)', 'value': 'MARROCOSMIRLEFT'},
					{'label': 'PERU (PACASMAYO - 7.4S 79.8W)', 'value': 'PACASMAYO'},
					{'label': 'USA (ELMERS ISLAND/LA - 29.17N 90.5W)', 'value': 'ELMERS'}
					# Adicione mais opções de local conforme necessário
				],
				value='SAOSEBASTIAO'
			),

			html.Br(),

			html.Label("Years selection:"),
			html.Div([
				dcc.Dropdown(
					id='start-year',
					options=[{'label': str(i), 'value': i} for i in range(1993, 2024)],
					value=1993,
				),
				html.Div(children='→', style={'margin': '0 10px'}),
				dcc.Dropdown(
					id='end-year',
					options=[{'label': str(i), 'value': i} for i in range(1993, 2024)],
					value=2023,
				),
			
				html.Div(children=' ', style={'margin': '0 10px'}),
				
			    # Botão flutuante para atualizar
				dbc.Button(
					"Update graphs",
					id="update-button",
					n_clicks=0,
					color="primary",
	#				className="float-button",
				),
			
			], style={'display': 'flex', 'alignItems': 'center'}),
	
			html.Br(),
			
			dbc.Tabs([
				dbc.Tab(label="Waves", tab_id="waves"),
				dbc.Tab(label="Wind", tab_id="wind"),
				dbc.Tab(label="Others", tab_id="other"),
			],
			id="tabs",
			active_tab="waves",
			),


			html.Div([
				dcc.Graph(id='monthly-stats-plot-alt', style={'width': '100%'}),
				dcc.Graph(id='monthly-stats-plot-dir', style={'width': '100%'}),
				dcc.Graph(id='monthly-stats-plot-per', style={'width': '100%'}),
				
				# Layout para as condições
				html.Div([
					html.Label("Cond. 1:		"),
					dcc.Input(id='altura1', type='number', placeholder='Height', style={'maxWidth': '80px'}),
					dcc.Input(id='periodo1', type='number', placeholder='Period', style={'maxWidth': '80px'}),
					dcc.Input(id='direcao1', type='text', placeholder='Dir (none = ALL)', style={'maxWidth': '120px'}),
				], style={'width': '100%', 'white-space': 'pre'}),
				html.Div([
					html.Label("OR Cond. 2:	"),
					dcc.Input(id='altura2', type='number', placeholder='Height', style={'maxWidth': '80px'}),
					dcc.Input(id='periodo2', type='number', placeholder='Period', style={'maxWidth': '80px'}),
					dcc.Input(id='direcao2', type='text', placeholder='Dir (none = ALL)', style={'maxWidth': '120px'}),
				], style={'width': '100%', 'white-space': 'pre'}),
				html.Div([
					html.Label("OR Cond. 3:	"),
					dcc.Input(id='altura3', type='number', placeholder='Height', style={'maxWidth': '80px'}),
					dcc.Input(id='periodo3', type='number', placeholder='Period', style={'maxWidth': '80px'}),
					dcc.Input(id='direcao3', type='text', placeholder='Dir (none = ALL)', style={'maxWidth': '120px'}),
				], style={'width': '100%', 'white-space': 'pre'}),
			
				dcc.Graph(id='custom-conditions-plot', style={'width': '100%'}),
				
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
				
				dcc.Graph(id='annual-stats-plot-alt', style={'width': '100%'}),
				dcc.Graph(id='annual-stats-plot-dir', style={'width': '100%'}),
				dcc.Graph(id='annual-stats-plot-per', style={'width': '100%'}),
			], id="waves-content", style={'display': 'block'}),
			
			
			html.Div([
			
				html.Br(),
				html.Label("Select the hours of the day to analyze"),
				html.Br(),
				html.Label("the wind (local time):"),

				# Caixas de seleção para os horários
				dcc.Checklist(
					id='horarios-checklist_wind',
					options=[
						{'label': f' {hora:02d}h   ', 'value': hora} for hora in [0, 3, 6, 9, 12, 15, 18, 21]
					],
					value=[0, 3, 6, 9, 12, 15, 18, 21],
					style={'white-space': 'pre'}
				),	
				
				dcc.Graph(id='monthly-stats-plot-int_wind', style={'width': '100%'}),
				dcc.Graph(id='rose_wind', style={'width': '100%'}),
				
				dcc.Graph(id='monthly-stats-plot-dir_wind', style={'width': '100%'}),
				dcc.Graph(id='monthly-stats-plot-dir_wind_t', style={'width': '100%'}),
				
			
				html.Div([
					html.Label("Select the month:"),
					dcc.Dropdown(
						id='month-dropdown_wind',
						options=[
							{'label': month, 'value': i+1} for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
						],
						value=1,
						style={'width': '100%', 'display': 'inline-block'}
					),
				]),
				
				dcc.Graph(id='annual-stats-plot-int_wind', style={'width': '100%'}),
				dcc.Graph(id='annual-stats-plot-dir_wind', style={'width': '100%'}),
				dcc.Graph(id='annual-stats-plot-dir_wind_t', style={'width': '100%'}),
			], id="wind-content", style={'display': 'none'}),	
			
			html.Div([
				html.Br(),
				html.Label("Select the hours of the day to analyze"),
				html.Br(),
				html.Label("the air temperature (local time):"),

				# Caixas de seleção para os horários
				dcc.Checklist(
					id='horarios-checklist_sst',
					options=[
						{'label': f' {hora:02d}h   ', 'value': hora} for hora in [0, 3, 6, 9, 12, 15, 18, 21]
					],
					value=[0, 3, 6, 9, 12, 15, 18, 21],
					style={'white-space': 'pre'}
				),

				dcc.Graph(id='other_anual_times', style={'width': '100%'}),
						
			], id="others-content", style={'display': 'none'}),
				
		]),
	]
)

# Callbacks para atualizar os gráficos e a guia ativa
@app.callback(
	[Output('monthly-stats-plot-alt', 'figure'),
	 Output('monthly-stats-plot-dir', 'figure'),
	 Output('monthly-stats-plot-per', 'figure'),
	 Output('custom-conditions-plot', 'figure'),
	 Output('annual-stats-plot-alt', 'figure'),
	 Output('annual-stats-plot-dir', 'figure'),
	 Output('annual-stats-plot-per', 'figure'),
	 Output('monthly-stats-plot-int_wind', 'figure'),
	 Output('rose_wind', 'figure'),
	 Output('monthly-stats-plot-dir_wind', 'figure'),
	 Output('monthly-stats-plot-dir_wind_t', 'figure'),
	 Output('annual-stats-plot-int_wind', 'figure'),
	 Output('annual-stats-plot-dir_wind', 'figure'),
	 Output('annual-stats-plot-dir_wind_t', 'figure'),
	 Output('other_anual_times', 'figure'),
	 Output('tabs', 'active_tab'),
	 Output('waves-content', 'style'),
	 Output('wind-content', 'style'),
	 Output('others-content', 'style')],
	[Input('update-button', 'n_clicks'),
	 Input('location-dropdown', 'value'),
	 Input('start-year', 'value'),
	 Input('end-year', 'value'),
	 Input('month-dropdown', 'value'),
	 Input('month-dropdown_wind', 'value'),
	 Input('altura1', 'value'),
	 Input('periodo1', 'value'),
	 Input('direcao1', 'value'),
	 Input('altura2', 'value'),
	 Input('periodo2', 'value'),
	 Input('direcao2', 'value'),
	 Input('altura3', 'value'),
	 Input('periodo3', 'value'),
	 Input('direcao3', 'value'),
	 Input("tabs", "active_tab"),
	 Input('horarios-checklist_wind', 'value'),
	 Input('horarios-checklist_sst', 'value')]
)
def update_plots(n_clicks, selected_location, start_year, end_year, selected_month, selected_month_wind, altura1, periodo1, direcao1, altura2, periodo2, direcao2, altura3, periodo3, direcao3, active_tab, selected_hours, selected_hours_others):

	#show_loading()
	anos = list(range(start_year, end_year + 1))
	# Carregar dados
	df = load_data(selected_location, anos)
	df_wind = load_data_wind(selected_location, anos)
	df_sst = load_data_sst(selected_location, anos)
	
	if active_tab == "waves":
		bins = [0, 1.0, 1.5, 2.0, 2.5, float('inf')]
		labels = ['< 1,0', '1,0-1,5', '1,5-2,0', '2,0-2,5', '> 2,5']
		parametro = 'VHM0'
		nome_parametro = 'Significant Wave Height (m)'

		bin_color_map = {
		'< 1,0': 'rgb(207,159,0)',
		'1,0-1,5': 'rgb(190,96,0)',
		'1,5-2,0': 'rgb(165,30,0)',
		'2,0-2,5': 'rgb(129,0,111)',
		'> 2,5': 'rgb(44,0,98)'}

		fig1 = plot_monthly_stats(df, anos, bins, labels, parametro, nome_parametro,bin_color_map)
		fig4 = plot_annual_stats(df, anos, selected_month, bins, labels, parametro, nome_parametro,bin_color_map)


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


		fig2 = plot_monthly_stats(df, anos, bins, labels, parametro, nome_parametro,bin_color_map)
		fig5 = plot_annual_stats(df, anos, selected_month, bins, labels, parametro, nome_parametro,bin_color_map)


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

		fig3 = plot_monthly_stats(df, anos, bins, labels, parametro, nome_parametro,bin_color_map)
		fig6 = plot_annual_stats(df, anos, selected_month, bins, labels, parametro, nome_parametro,bin_color_map)


		
		# Condições do usuário
		conditions = [{'altura': altura1, 'periodo': periodo1, 'direcao': direcao1},
		{'altura': altura2, 'periodo': periodo2, 'direcao': direcao2},
		{'altura': altura3, 'periodo': periodo3, 'direcao': direcao3}]
		
		fig_custom_conditions = plot_custom_conditions_frequency(df, conditions, anos)
		

		return [fig1, fig2, fig3, fig_custom_conditions, fig4, fig5, fig6, go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), active_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}]


	elif active_tab == "wind":
		bins = [0, 6, 12, 15, 18, 21, 25, 30, float('inf')]
		labels = ['< 6', '6-12', '12-15', '15-18', '18-21', '21-25', '25-30', '> 30']
		parametro = 'int'
		nome_parametro = 'Wind speed (knots)'

		bin_color_map = {
		'< 6': 'rgb(165,218,240)',
		'6-12': 'rgb(48,108,142)',
		'12-15': 'rgb(0,255,0)',
		'15-18': 'rgb(241,230,78)',
		'18-21': 'rgb(255,100,44)',
		'21-25': 'rgb(255,10,40)',
		'25-30': 'rgb(255,0,255)',
		'> 30': 'rgb(143,10,40)'}

		fig1_w = plot_monthly_stats(df_wind, anos, bins, labels, parametro, nome_parametro,bin_color_map,selected_hours)
		fig4_w = plot_annual_stats(df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map)
		
		
		bins = ['N', 'NE', 'NW', 'E', 'W', 'SW', 'SE', 'S']
		
		labels = bins
		
		parametro = 'CardinalDirection'
		nome_parametro = 'Wind direction'

		bin_color_map = {
		'N': 'rgb(24,0,33)',
		'NE': 'rgb(60,15,111)',
		'E': 'rgb(67,78,150)',
		'SE': 'rgb(102,138,162)',
		'S': 'rgb(181,180,186)',
		'SW': 'rgb(171,135,111)',
		'W': 'rgb(148,64,54)',
		'NW': 'rgb(109,15,51)'}
		
		fig2a_w = plot_monthly_stats(df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_hours)
		fig5a_w = plot_annual_stats(df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map)
		
		
		onshore, offshore, side, side_onshore, side_offshore = wind_type(selected_location);

		# Adiciona a coluna 'WindType'
		df_wind = add_wind_type_column(df_wind, onshore, side_onshore, offshore, side_offshore, side)

		bins = ['onshore','side-onshore','offshore','side-offshore','side']
		
		labels = bins
		
		parametro = 'WindType'
		nome_parametro = 'Wind type direction'

		bin_color_map = {
		'onshore': 'rgb(109,15,51)',
		'side-onshore': 'rgb(171,135,111)',
		'side': 'rgb(181,180,186)',
		'offshore': 'rgb(67,78,150)',
		'side-offshore': 'rgb(102,138,162)'}
		
		unique_categories_df = df_wind['WindType'].unique()

		# Filtrar bin_color_map para incluir apenas categorias existentes
		bin_color_map_filtered = {category: bin_color_map[category] for category in unique_categories_df}

		# Usar bin_color_map_filtered em vez do original
		bin_color_map = bin_color_map_filtered
		
		fig2_w = plot_monthly_stats(df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_hours)
		fig5_w = plot_annual_stats(df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map)
		
		rose_w = plot_rose()

		return [go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), fig1_w, rose_w, fig2a_w, fig2_w, fig4_w, fig5a_w, fig5_w, go.Figure(), active_tab, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}]


	elif active_tab == "other":
		
		fig_other_times = plot_others(df_wind, df_sst, anos, selected_hours_others)
		
		
		return [go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), fig_other_times, active_tab, {'display': 'none'}, {'display': 'none'}, {'display': 'block'}]

	
# Callback para atualizar dinamicamente os rótulos dos horários
@app.callback(
	[Output('horarios-checklist_wind', 'options'),
	Output('horarios-checklist_sst', 'options')],
	[Input('location-dropdown', 'value')]
	)
def update_horarios_labels(selected_location):
    
	if selected_location == 'JERICOACOARA':
		horario_gmt = -3

	if selected_location == 'SAOSEBASTIAO': 
		horario_gmt = -3

	if selected_location == 'CRICANORTE':
		horario_gmt = -6

	if selected_location == 'CRICASUL':
		horario_gmt = -6

	if selected_location == 'ELSALVADOR':
		horario_gmt = -6

	if selected_location == 'MARROCOSKAOKI':
		horario_gmt = +1

	if selected_location == 'MARROCOSTAGHAZOUT':
		horario_gmt = +1

	if selected_location == 'MARROCOSMIRLEFT':
		horario_gmt = +1

	if selected_location == 'PACASMAYO':
		horario_gmt = -5

	if selected_location == 'ELMERS':
		horario_gmt = -5

	
	horarios_convertidos = converter_horarios_gmt(np.array([0,3,6,9,12,15,18,21]), horario_gmt)
	horarios_atualizados = [{'label': f' {hora:02d}h   ', 'value': original} for hora, original in zip(horarios_convertidos, np.array([0,3,6,9,12,15,18,21]))]


	horarios_convertidos_2 = converter_horarios_gmt(np.array([0,3,6,9,12,15,18,21]), horario_gmt)
	horarios_atualizados_2 = [{'label': f' {hora:02d}h   ', 'value': original} for hora, original in zip(horarios_convertidos, np.array([0,3,6,9,12,15,18,21]))]



	return horarios_atualizados, horarios_atualizados_2
	
	#hide_loading()

if __name__ == '__main__':
	app.run_server(debug=True)
