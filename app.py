import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import plotly.graph_objs as go

from funcoes_app import load_data, plot_monthly_stats, plot_annual_stats, plot_custom_conditions_frequency, plot_others, plot_annual_stats_others, plot_rose, add_wind_type_column, wind_type, converter_horarios_gmt

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.themes.SPACELAB,dbc.icons.FONT_AWESOME])
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

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

app.layout = dbc.Accordion([
				dbc.AccordionItem(

					dcc.Loading(
						id="loading-container",
						type='dot',
						fullscreen=True,
						color='rgba(64,183,173,1)',
						style={'backgroundColor': None},
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
									#dbc.Button(
									#	"Update graphs",
									#	id="update-button",
									#	n_clicks=0,
									#	color="secondary",
						#				className="float-button",
									#),
								
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
									
									html.Div([
										html.Label("Cond. 1:		"),
										dcc.Input(id='altura1', type='number', placeholder='Height', style={'maxWidth': '80px'}),
										dcc.Input(id='periodo1', type='number', placeholder='Period', style={'maxWidth': '80px'}),
										dcc.Input(id='direcao1', type='text', placeholder='Dir (none = ALL)', style={'maxWidth': '120px'}),
									], style={'width': '100%', 'white-space': 'pre'}, id='pega_tamanho'),
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
									html.Label("Select the hours of the day to analyze the wind"),
									html.Br(),
									html.Label("(local time - more than one = average):"),

									dcc.Dropdown(
										id='horarios-checklist_wind',
										options=[
											{'label': f' {hora:02d}h   ', 'value': hora} for hora in [0, 3, 6, 9, 12, 15, 18, 21]
										],
										value=[],
										multi=True,
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
									html.Label("Select the hours of the day to analyze the air"),
									html.Br(),
									html.Label("temperature (local time - more than one = average):"),

									dcc.Dropdown(
										id='horarios-checklist_sst',
										options=[
											{'label': f' {hora:02d}h   ', 'value': hora} for hora in [0, 3, 6, 9, 12, 15, 18, 21]
										],
										value=[],
										multi=True,
										style={'white-space': 'pre'}
									),
									
									html.Br(),
									dcc.Graph(id='other_anual_times', style={'width': '100%'}),
									html.Br(),
									
									html.Div([
										html.Label("Select the month:"),
										dcc.Dropdown(
											id='month-dropdown_others',
											options=[
												{'label': month, 'value': i+1} for i, month in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
											],
											value=1,
											style={'width': '100%', 'display': 'inline-block'}
										),
									]),
									
									dcc.Graph(id='annual-stats-plot-prec', style={'width': '100%'}),
									dcc.Graph(id='annual-stats-plot-temp', style={'width': '100%'}),
									dcc.Graph(id='annual-stats-plot-sst', style={'width': '100%'}),
											
								], id="others-content", style={'display': 'none'}),
									
							]),
						]
					),
					title="Data",
				),
				dbc.AccordionItem(
					"This is the content of the second section",
					title="About",
				),
				dbc.AccordionItem(
					html.A(
						dbc.Row(
							[
								dbc.Col(dbc.NavbarBrand("hpgregorio.net", className="ms-2")),
							],
							align="center",
							className="g-0",
						),
						href="https://hpgregorio.net",
						style={"textDecoration": "none",'backgroundColor': 'rgba(244,241,214,1)'},
					),
					title="Contact",
				),
			],flush=True,start_collapsed=True)

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
	 Output('annual-stats-plot-prec', 'figure'),
	 Output('annual-stats-plot-temp', 'figure'),
	 Output('annual-stats-plot-sst', 'figure'),
	 Output('tabs', 'active_tab'),
	 Output('waves-content', 'style'),
	 Output('wind-content', 'style'),
	 Output('others-content', 'style')],
	#[Input('update-button', 'n_clicks'),
	[Input('location-dropdown', 'value'),
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
	 Input('horarios-checklist_sst', 'value'),
	 Input('month-dropdown_others', 'value')]
)
#def update_plots(n_clicks, selected_location, start_year, end_year, selected_month, selected_month_wind, altura1, periodo1, direcao1, altura2, periodo2, direcao2, altura3, periodo3, direcao3, active_tab, selected_hours, selected_hours_others, selected_month_others):
def update_plots(selected_location, start_year, end_year, selected_month, selected_month_wind, altura1, periodo1, direcao1, altura2, periodo2, direcao2, altura3, periodo3, direcao3, active_tab, selected_hours, selected_hours_others, selected_month_others):

	#n_cliks = None
	#if n_clicks is None:
	#	raise PreventUpdate
	#else:
		anos = list(range(start_year, end_year + 1))

		df = load_data(selected_location, anos, 'ONDAS')
		df_wind = load_data(selected_location, anos, 'VENTOS')
		df_sst = load_data(selected_location, anos, 'SST')
		
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

			conditions = [{'altura': altura1, 'periodo': periodo1, 'direcao': direcao1},
			{'altura': altura2, 'periodo': periodo2, 'direcao': direcao2},
			{'altura': altura3, 'periodo': periodo3, 'direcao': direcao3}]
			
			fig_custom_conditions = plot_custom_conditions_frequency(df, conditions, anos)

			return [fig1, fig2, fig3, fig_custom_conditions, fig4, fig5, fig6, go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), active_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}]

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
			fig4_w = plot_annual_stats(df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map, selected_hours)
			
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
			fig5a_w = plot_annual_stats(df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map, selected_hours)
			
			onshore, offshore, side, side_onshore, side_offshore = wind_type(WIND_TYPES,selected_location);

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
			fig5_w = plot_annual_stats(df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map, selected_hours)
			
			rose_w = plot_rose()

			return [go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), fig1_w, rose_w, fig2a_w, fig2_w, fig4_w, fig5a_w, fig5_w, go.Figure(), go.Figure(), go.Figure(), go.Figure(), active_tab, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}]

		elif active_tab == "other":
			
			fig_other = plot_others(df_wind, df_sst, anos, selected_location, selected_hours_others)
			
			fig_other_prec = plot_annual_stats_others(df_wind, anos, selected_month_others, 'prec', 'Precipitation')
			
			fig_other_temp = plot_annual_stats_others(df_wind, anos, selected_month_others, 'temp', 'Air Temp', selected_hours_others)
			
			fig_other_sst = plot_annual_stats_others(df_wind, anos, selected_month_others, 'sst', 'Sea Temp')
			
			return [go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), fig_other, fig_other_prec, fig_other_temp, fig_other_sst, active_tab, {'display': 'none'}, {'display': 'none'}, {'display': 'block'}]
	
# Callback para atualizar dinamicamente os rótulos dos horários
@app.callback(
	[Output('horarios-checklist_wind', 'options'),
	Output('horarios-checklist_sst', 'options')],
	[Input('location-dropdown', 'value')]
	)
def update_horarios_labels(selected_location):
	horario_original = [0, 3, 6, 9, 12, 15, 18, 21];
	horario_gmt = TIME_ZONES.get(selected_location, 0)
	
	horarios_convertidos = converter_horarios_gmt(horario_original, horario_gmt)
	horarios_atualizados = [{'label': f' {hora:02d}h   ', 'value': original} for hora, original in zip(horarios_convertidos, horario_original)]

	return horarios_atualizados, horarios_atualizados
	
if __name__ == '__main__':
	app.run_server(debug=True)
