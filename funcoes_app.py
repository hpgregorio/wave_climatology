import pandas as pd
from numpy import select
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def load_data(location, years, type):
	dataframes_list = []

	for year in years:
		
		if type == 'ONDAS':
			filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/csv/ONDAS_{location}_{year}.csv"
			#filename_csv = f"csv/ONDAS_{location}_{year}.csv"
		
		elif type == 'VENTOS':
			filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/ventos_csv/VENTOS_{location}_{year}.csv"
			#filename_csv = f"ventos_csv/VENTOS_{location}_{year}.csv"
			
		elif type == 'SST':
			filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/sst_csv/SST_{location}_{year}.csv"
			#filename_csv = f"sst_csv/SST_{location}_{year}.csv"
		
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

		height_distribution = df_selected_hours.groupby([df_selected_hours['Datetime'].dt.month, 'Range'])[parametro].count().unstack()

	else:
		if parametro == 'CardinalDirection' or parametro == 'WindType':
			df['Range'] = pd.Categorical(df[parametro], categories=bins, ordered=True)
		else:
			df['Range'] = pd.cut(df[parametro], bins=bins, labels=labels, right=False)

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

def plot_annual_stats(df, selected_years, mes, bins, labels, parametro, nome_parametro, bin_color_map, selected_hours=None):

	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		month_data = df_selected_hours[df_selected_hours['Datetime'].dt.month == mes]
		
	else:
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

def plot_others(df, df_sst, selected_years, selected_location, selected_hours=None):

	tit = {'JERICOACOARA' : 'Jericoacoara/CE (Brazil)',
		'SAOSEBASTIAO' : 'São Sebastião/SP (Brazil)',
		'CRICANORTE' : 'Guanacaste (Costa Rica)',
		'CRICASUL' : 'Peninsula Osa (Costa Rica)',
		'ELSALVADOR' : 'El Tunco (El Salvador)',
		'MARROCOSKAOKI' : 'Sidi Kaoki (Morrocco)',
		'MARROCOSTAGHAZOUT' : 'Taghazout (Morrocco)',
		'MARROCOSMIRLEFT' : 'Mirleft (Morrocco)',
		'PACASMAYO' : 'Pacasmayo (Peru)',
		'ELMERS' : 'Elmers Island/LA (USA)'}
	
	if selected_years != list(range(1993, 2023 + 1)):
		#####
		#historic data
		#####
		df_sst_hist = load_data(selected_location, list(range(1993, 2023 + 1)), 'SST')
		df_sst_hist['Month'] = df_sst_hist['Datetime'].dt.month
		df_sst_hist['Year'] = df_sst_hist['Datetime'].dt.year
		
		df_temp_hist = load_data(selected_location, list(range(1993, 2023 + 1)), 'VENTOS')
		df_temp_hist['Month'] = df_temp_hist['Datetime'].dt.month
		df_temp_hist['Year'] = df_temp_hist['Datetime'].dt.year
		
		if selected_hours is not None:
			df_selected_hours = df_temp_hist[df_temp_hist['Datetime'].dt.hour.isin(selected_hours)]
			df_selected_hours['Month'] = df_selected_hours['Datetime'].dt.month
			df_selected_hours['Year'] = df_selected_hours['Datetime'].dt.year
			
			monthly_temp_avg_hist = df_selected_hours.groupby('Month')['temp'].mean()
			monthly_temp_std_hist = df_selected_hours.groupby('Month')['temp'].std()
			
			hours_tit = 'h , '.join(['%1.0f' % val for val in selected_hours])
		else:
			monthly_temp_avg_hist = df_temp_hist.groupby('Month')['temp'].mean()
			monthly_temp_std_hist = df_temp_hist.groupby('Month')['temp'].std()

		monthly_sst_avg_hist = df_sst_hist.groupby('Month')['sst'].mean()
		monthly_sst_std_hist = df_sst_hist.groupby('Month')['sst'].std()

		
		#PRECIPITAÇÃO - precisa somar todos os dados do mês - dados dão a precipitação a cada 3h - grafico é precipitação/mês
		
		# Agrupe os dados por ano e mês, somando a coluna 'prec' - o resultado é a precipitação total mensal ao longo dos anos
		monthly_prec_sum = df_temp_hist.groupby(['Year', 'Month'])['prec'].sum().reset_index()
		
		# Calcule a média mensal ao longo dos anos
		monthly_prec_avg = monthly_prec_sum.groupby('Month')['prec'].mean().reset_index()
		monthly_prec_avg_hist = monthly_prec_avg*1000 #transformar para mm/mês (dado original está em m)
		
		#####
		#####
		#####
		
	df['Month'] = df['Datetime'].dt.month
	df['Year'] = df['Datetime'].dt.year
	
	df_sst['Month'] = df_sst['Datetime'].dt.month
	df_sst['Year'] = df_sst['Datetime'].dt.year

	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		df_selected_hours['Month'] = df_selected_hours['Datetime'].dt.month
		df_selected_hours['Year'] = df_selected_hours['Datetime'].dt.year
		
		monthly_temp_avg = df_selected_hours.groupby('Month')['temp'].mean()
		
		hours_tit = 'h , '.join(['%1.0f' % val for val in selected_hours])
	else:
		monthly_temp_avg = df.groupby('Month')['temp'].mean()

	monthly_sst_avg = df_sst.groupby('Month')['sst'].mean()
	
	#PRECIPITAÇÃO - precisa somar todos os dados do mês - dados dão a precipitação a cada 3h - grafico é precipitação/mês
	
	# Agrupe os dados por ano e mês, somando a coluna 'prec' - o resultado é a precipitação total mensal ao longo dos anos
	monthly_prec_sum = df.groupby(['Year', 'Month'])['prec'].sum().reset_index()
	
	# Calcule a média mensal ao longo dos anos
	monthly_prec_avg = monthly_prec_sum.groupby('Month')['prec'].mean().reset_index()
	monthly_prec_avg = monthly_prec_avg*1000 #transformar para mm/mês (dado original está em m)
	
	
	
	
	
	month_names = ['Jan', 'Feb', 'Mar' , 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	if selected_years[0] == selected_years[-1]:
		title_years = f"{selected_years[0]}"
	else:
		title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	
	if selected_years != list(range(1993, 2023 + 1)):

		fig = make_subplots(rows=3, cols=1, shared_xaxes=False, subplot_titles=[f'{tit.get(selected_location, 0)}', ''], vertical_spacing=0.05)
		
		# Adicione barras para precipitação primeiro
		trace_prec = go.Bar(
			x=month_names,
			y=monthly_prec_avg['prec'],
			name='Precipitation (%s)'%title_years,
			marker=dict(color='rgba(64,183,173,1)')
		)
		
		# Adicione barras para precipitação primeiro
		trace_prec_hist = go.Bar(
			x=month_names,
			y=monthly_prec_avg_hist['prec'],
			name='Historic Precipitation (1993 to 2023)',
			marker=dict(color='rgba(0, 0, 0, 0.2)')
		)

		# Adicione os traços de linha
		trace_temp_hist = go.Scatter(
			x=month_names,
			y=monthly_temp_avg_hist,
			mode='lines',
			name='Historic Air Temp (%sh - 1993 to 2023)'%(hours_tit),
			line=dict(color='rgb(67, 78, 150)', dash='dot'),
			
		)
		
		upper_bound = [avg + std for avg, std in zip(monthly_temp_avg_hist, monthly_temp_std_hist)]
		lower_bound = [avg - std for avg, std in zip(monthly_temp_avg_hist, monthly_temp_std_hist)]

		
		trace_temp_area = go.Scatter(
			x=month_names + month_names[::-1],  # Concatenate month_names with its reverse
			y=upper_bound + lower_bound[::-1],
			fill='toself',  # Indicates to fill the area
			fillcolor='rgba(67, 78, 150, 0.2)',  # Color and transparency of the filled area
			line=dict(color='rgba(255, 255, 255, 0)'),  # Hide the line of the area trace
			showlegend=False,  # Do not show legend for the area trace
			
		)
		
		trace_temp = go.Scatter(
			x=month_names,
			y=monthly_temp_avg,
			mode='lines+markers',
			name='Air Temp (%sh - %s)'%(hours_tit,title_years),
			line=dict(color='rgb(67, 78, 150)'),
			
		)

		trace_sst_hist = go.Scatter(
			x=month_names,
			y=monthly_sst_avg_hist,
			mode='lines',
			name='Historic Sea Temp (1993 to 2023)',
			line=dict(color='rgb(220, 20, 60)', dash='dot'),
			
		)
		
		upper_bound = [avg + std for avg, std in zip(monthly_sst_avg_hist, monthly_sst_std_hist)]
		lower_bound = [avg - std for avg, std in zip(monthly_sst_avg_hist, monthly_sst_std_hist)]

		
		trace_sst_area = go.Scatter(
			x=month_names + month_names[::-1],  # Concatenate month_names with its reverse
			y=upper_bound + lower_bound[::-1],
			fill='toself',  # Indicates to fill the area
			fillcolor='rgba(220, 20, 60, 0.2)',  # Color and transparency of the filled area
			line=dict(color='rgba(255, 255, 255, 0)'),  # Hide the line of the area trace
			showlegend=False,  # Do not show legend for the area trace
			
		)

		trace_sst = go.Scatter(
			x=month_names,
			y=monthly_sst_avg,
			mode='lines+markers',
			name='Sea Temp (%s)'%title_years,
			line=dict(color='rgb(220, 20, 60)'),
			
		)

		fig.update_layout(
			
			yaxis=dict(title='Precipitation (mm/month)'),# range=[0, 200]),
			yaxis2=dict(title='Air Temp (°C)'),
			yaxis3=dict(title='Sea Temp (°C)'),
			plot_bgcolor='white',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001,
			yaxis2_gridcolor='lightgray',
			yaxis2_gridwidth=0.0001,
			yaxis3_gridcolor='lightgray',
			yaxis3_gridwidth=0.0001,
			height=300*3,
			width=400,
			margin=dict(l=10, r=10, t=40, b=10),
			legend=dict(
				x=-0.15,
				y=-0.05,
				orientation='h',
				bgcolor='rgba(255, 255, 255, 0)',
				traceorder='normal',  # Ordem padrão de exibição dos itens da legenda
				bordercolor='rgba(255, 255, 255, 0)',  # Cor da borda da legenda (transparente)
				borderwidth=0,  # Largura da borda da legenda
				xanchor='left',  # Ancoragem horizontal no centro
				yanchor='top'  # Ancoragem vertical no topo
			)
		)
		
		fig.add_trace(trace_prec_hist, row=1, col=1)
		fig.add_trace(trace_prec, row=1, col=1)
		fig.add_trace(trace_temp_area, row=2, col=1)
		fig.add_trace(trace_temp_hist, row=2, col=1)
		fig.add_trace(trace_temp, row=2, col=1)
		fig.add_trace(trace_sst_area, row=3, col=1)
		fig.add_trace(trace_sst_hist, row=3, col=1)
		fig.add_trace(trace_sst, row=3, col=1)

	else:
		fig = go.Figure()
		
		trace_prec = go.Bar(
			x=month_names,
			y=monthly_prec_avg['prec'],
			name='Precipitation (%s)'%title_years,
			marker=dict(color='rgba(0, 0, 0, 0.2)')
		)
		
		trace_temp = go.Scatter(
			x=month_names,
			y=monthly_temp_avg,
			mode='lines+markers',
			name='Air Temp (%sh - %s)'%(hours_tit,title_years),
			line=dict(color='rgb(67, 78, 150)'),
			yaxis='y2'
		)

		trace_sst = go.Scatter(
			x=month_names,
			y=monthly_sst_avg,
			mode='lines+markers',
			name='Sea Temp (%s)'%title_years,
			line=dict(color='rgb(220, 20, 60)'),
			yaxis='y2'
		)

		fig.update_layout(
			title=f'{tit.get(selected_location, 0)}',
			yaxis=dict(title='Precipitation (mm/month)'),# range=[0, 200]),
			yaxis2=dict(
				title='Temperature (°C)',
				overlaying='y',
				side='right',
				#range=[12, 32]
			),
			plot_bgcolor='white',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001,
			height=350,
			width=400,
			margin=dict(l=10, r=10, t=40, b=10),
			legend=dict(
				x=0,
				y=-0.15,
				orientation='h',
				bgcolor='rgba(255, 255, 255, 0)',
				traceorder='normal',  # Ordem padrão de exibição dos itens da legenda
				bordercolor='rgba(255, 255, 255, 0)',  # Cor da borda da legenda (transparente)
				borderwidth=0,  # Largura da borda da legenda
				xanchor='left',  # Ancoragem horizontal no centro
				yanchor='top'  # Ancoragem vertical no topo
			)
		)
	
	
		fig.add_trace(trace_prec)
		fig.add_trace(trace_temp)
		fig.add_trace(trace_sst)
	
	
	return fig
	


def plot_annual_stats_others(df, selected_years, mes, parametro, nome_parametro, selected_hours=None):

	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		month_data = df_selected_hours[df_selected_hours['Datetime'].dt.month == mes]
		
	else:
		month_data = df[df['Datetime'].dt.month == mes]

	month_data['Year'] = month_data['Datetime'].dt.year
	month_data['Month'] = month_data['Datetime'].dt.month
	
	if parametro == 'prec': 
		monthly_prec_sum = month_data.groupby(['Year'])['prec'].sum().reset_index()
		montly_average_year = monthly_prec_sum *1000
	
	else:
		montly_average_year = month_data.groupby(['Year', month_data['Datetime'].dt.month])[parametro].mean()
		montly_average_year = montly_average_year.reset_index()
	
	years = list(selected_years)
	month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	title_month = f"{month_names[mes-1]}"

	fig = go.Figure()
	
	if parametro == 'prec':
		titulo = 'Precipitation (mm/month)';
		limites = [0, 200]
		trace = go.Bar(
			x=years,
			y=montly_average_year[parametro],
			name=nome_parametro,
			marker=dict(color='rgb(200, 200, 200)')
		)

	else:
		if parametro == 'temp': 
			line_color = 'rgb(67, 78, 150)'
			titulo = 'Air Temperature (°C)'
		if parametro == 'sst': 
			line_color = 'rgb(220, 20, 60)'
			titulo = 'Sea Temperature (°C)'
		
		limites = [12, 32]
		trace = go.Scatter(
			x=years,
			y=montly_average_year[parametro],
			mode='lines+markers',
			name=nome_parametro,
			line=dict(color=line_color)
		)

	# Adicione os traços ao gráfico
	fig.add_trace(trace)
	
	layout = go.Layout(
		title=f'{nome_parametro} - {title_month}',
		yaxis=dict(title=titulo, range=limites),
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
	
	years_ticks = list(selected_years)
	layout.update(xaxis=dict(tickvals=years_ticks, ticktext=years_ticks, tickfont=dict(size=8)))

	fig = go.Figure(data=[trace], layout=layout)
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
	df['WindType'] = select(conditions, choices, default=None)
	return df		

def wind_type(WIND_TYPES,selected_location):
    return (
        WIND_TYPES[selected_location]['onshore'],
        WIND_TYPES[selected_location]['offshore'],
        WIND_TYPES[selected_location]['side'],
        WIND_TYPES[selected_location]['side_onshore'],
        WIND_TYPES[selected_location]['side_offshore'],
    )
	
# Função para converter os horários de acordo com o GMT específico
def converter_horarios_gmt(horarios, gmt):
	horarios_convertidos = [(hora + gmt) % 24 for hora in horarios]
	return horarios_convertidos