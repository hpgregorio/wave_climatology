import pandas as pd
from numpy import select
import plotly.graph_objs as go

def load_data(location, years, type):
	dataframes_list = []

	for year in years:
		
		if type == 'ONDAS':
			#filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/csv/ONDAS_{location}_{year}.csv"
			filename_csv = f"csv/ONDAS_{location}_{year}.csv"
		
		elif type == 'VENTOS':
			#filename_csv = f"https://raw.githubusercontent.com/hpgregorio/wave_climatology/master/ventos_csv/VENTOS_{location}_{year}.csv"
			filename_csv = f"ventos_csv/VENTOS_{location}_{year}.csv"
			
		elif type == 'SST':
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