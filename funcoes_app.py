import pandas as pd
from numpy import select
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import timedelta
import requests
import io

def load_data(location, years, type, df_locais):
	gmt_offset = df_locais[df_locais['location'] == location]['time_zone'].values
	gmt_offset = gmt_offset.item()

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
		df['Datetime'] = df['Datetime'] + timedelta(hours=+gmt_offset)
		dataframes_list.append(df)
	return pd.concat(dataframes_list, ignore_index=True)
	
def plot_monthly_stats(df_locais, df, selected_years, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours=None):
	tit = str(df_locais[df_locais['location'] == selected_location]['title'].values[0])
	
	if selected_years[0] == selected_years[-1]:
		title_years = f"{selected_years[0]}"
	else:
		title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		# Criando uma coluna no dataframe para representar o intervalo de altura
		if parametro == 'CardinalDirection' or parametro == 'WindType':
			df_selected_hours['Range'] = pd.Categorical(df_selected_hours[parametro], categories=bins, ordered=True)
		else:
			df_selected_hours['Range'] = pd.cut(df_selected_hours[parametro], bins=bins, labels=labels, right=False)
		height_distribution = df_selected_hours.groupby([df_selected_hours['Datetime'].dt.month, 'Range'])[parametro].count().unstack()
		hours_tit = ':00 , '.join(['%1.0f' % val for val in selected_hours])
		titul = f'{tit}<br>{nome_parametro} - {title_years} ({hours_tit}:00)'
	else:
		if parametro == 'CardinalDirection' or parametro == 'WindType':
			df['Range'] = pd.Categorical(df[parametro], categories=bins, ordered=True)
		else:
			df['Range'] = pd.cut(df[parametro], bins=bins, labels=labels, right=False)
		height_distribution = df.groupby([df['Datetime'].dt.month, 'Range'])[parametro].count().unstack()
		titul = f'{tit}<br>{nome_parametro} - {title_years}'
	# Calculando a porcentagem da distribuição
	height_distribution_percentage = height_distribution.div(height_distribution.sum(axis=1), axis=0) * 100
	month_names = ['Jan', 'Feb', 'Mar' , 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	# Criando o gráfico de barras
	traces = []
	for col in height_distribution_percentage.columns:
		trace = go.Bar(
			x=month_names,
			y=height_distribution_percentage[col],
			name=f'{col}',
			marker=dict(color=bin_color_map[col])
		)
		traces.append(trace)
	if parametro=='CardinalDirection':
		layout = go.Layout(
			showlegend=False,
			title=dict(text=titul,font=dict(size=15)),
			yaxis=dict(title='Occurency (%)', range=[0, 100]),
			barmode='stack',
			height=330,
			width=350,
			margin=dict(l=10, r=10, t=80, b=10),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001
		)
	else:
		layout = go.Layout(
			title=dict(text=titul,font=dict(size=15)),
			yaxis=dict(title='Occurency (%)', range=[0, 100]),
			legend=dict(
				x=-0.15,
				y=-0.15,
				orientation='h',
				title='',
				font=dict(size=10)
			),
			barmode='stack',
			height=380,
			width=350,
			margin=dict(l=10, r=10, t=80, b=10),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001
		)
	fig = go.Figure(data=traces, layout=layout)
	return fig

def plot_annual_stats(df_locais, df, selected_years, mes, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours=None):
	tit = str(df_locais[df_locais['location'] == selected_location]['title'].values[0])
	years = list(selected_years)  # Converter para lista
	month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	title_month = f"{month_names[mes-1]}"

	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		month_data = df_selected_hours[df_selected_hours['Datetime'].dt.month == mes]
		hours_tit = ':00 , '.join(['%1.0f' % val for val in selected_hours])
		titul = f'{tit}<br>{nome_parametro} - {title_month} ({hours_tit}:00)'
	else:
		month_data = df[df['Datetime'].dt.month == mes]
		titul = f'{tit}<br>{nome_parametro} - {title_month}'
	if parametro == 'CardinalDirection' or parametro == 'WindType':
		month_data['Range'] = pd.Categorical(month_data[parametro], categories=bins, ordered=True)
	else:
		month_data['Range'] = pd.cut(month_data[parametro], bins=bins, labels=labels, right=False)
	month_height_distribution = month_data.groupby([month_data['Datetime'].dt.year, 'Range'])[parametro].count().unstack()
	month_height_distribution_percentage = month_height_distribution.div(month_height_distribution.sum(axis=1), axis=0) * 100
	#Grafico
	traces = []
	for col in month_height_distribution_percentage.columns:
		trace = go.Bar(
			x=years,
			y=month_height_distribution_percentage[col],
			name=f'{col}',
			marker=dict(color=bin_color_map[col])
		)
		traces.append(trace)
	if parametro=='CardinalDirection':
		layout = go.Layout(
			showlegend=False,
			title=dict(text=titul,font=dict(size=15)),
			yaxis=dict(title='Occurency (%)', range=[0, 100]),
			barmode='stack',
			height=330,
			width=350,
			margin=dict(l=10, r=10, t=80, b=10),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001
		)
	else:
		layout = go.Layout(
			title=dict(text=titul,font=dict(size=15)),
			yaxis=dict(title='Occurency (%)', range=[0, 100]),
			legend=dict(
				x=-0.15,
				y=-0.15,
				orientation='h',
				title='',
				font=dict(size=10)
			),
			barmode='stack',
			height=380,
			width=350,
			margin=dict(l=10, r=10, t=80, b=10),
			plot_bgcolor='rgba(255,255,255,0)',
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
	
	if conditions[0]['direcao'] is not None:
		title_trace = f"Waves with significant height equal to or greater <br>than {conditions[0]['altura']} m and period equal to or greater than {conditions[0]['periodo']} s,<br>coming from direction {conditions[0]['direcao']}"
	else:
		title_trace = f"Waves with significant height equal to or greater <br>than {conditions[0]['altura']} m and period equal to or greater than {conditions[0]['periodo']} s,<br>coming from any direction"
		
	fig = go.Figure()
	
	# Criando o gráfico de barras
	trace = go.Bar(
		x=month_names,
		y=monthly_condition_percentage,
		marker=dict(color='rgb(67, 78, 150)'),
		name=title_trace,
		showlegend = True
	)
	
	fig.add_trace(trace)
	
	fig.update_layout(
		title=dict(text=f'Occurency according with the conditions<br>- {title_years}',font=dict(size=15)),
		yaxis=dict(title='Occurency (%)', range=[0, 100]),
		plot_bgcolor='rgba(255,255,255,0)',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.5,
		height=350,
		width=350,
		margin=dict(l=10, r=10, t=70, b=0),
		legend=dict(
				x=-0.15,
				y=-0.2,
				orientation='h',
				bgcolor='rgba(255, 255, 255, 0)',
				traceorder='normal',  # Ordem padrão de exibição dos itens da legenda
				bordercolor='rgba(255, 255, 255, 0)',  # Cor da borda da legenda (transparente)
				borderwidth=0,  # Largura da borda da legenda
				xanchor='left',  # Ancoragem horizontal no centro
				yanchor='top'  # Ancoragem vertical no topo
			)
	)

	
	return fig




def plot_others(df_locais, df, df_sst, selected_years, selected_location, selected_hours, prec_kind):

	tit = str(df_locais[df_locais['location'] == selected_location]['title'].values[0])
		
	if selected_years != list(range(1993, 2025 + 1)):
		#####
		#historic data
		#####
		df_sst_hist = load_data(selected_location, list(range(1993, 2025 + 1)), 'SST', df_locais)
		df_sst_hist['Month'] = df_sst_hist['Datetime'].dt.month
		df_sst_hist['Year'] = df_sst_hist['Datetime'].dt.year
		
		df_temp_hist = load_data(selected_location, list(range(1993, 2025 + 1)), 'VENTOS', df_locais)
		df_temp_hist['Month'] = df_temp_hist['Datetime'].dt.month
		df_temp_hist['Year'] = df_temp_hist['Datetime'].dt.year
		
		if selected_hours is not None:
			df_selected_hours = df_temp_hist[df_temp_hist['Datetime'].dt.hour.isin(selected_hours)]
			df_selected_hours['Month'] = df_selected_hours['Datetime'].dt.month
			df_selected_hours['Year'] = df_selected_hours['Datetime'].dt.year
			
			monthly_temp_avg_hist = df_selected_hours.groupby('Month')['temp'].mean()
			monthly_temp_std_hist = df_selected_hours.groupby('Month')['temp'].std()
			
			hours_tit = ':00 , '.join(['%1.0f' % val for val in selected_hours])
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
		monthly_prec_avg_hist = monthly_prec_avg['prec']*3000 #transformar para mm/mês (dado original está em m e em horas - dados a cada 3h (tranforma em 24 multiplicando por 3)
		
		
		if prec_kind == 'perc':
			#precipitacao -- porcentagem de dias com chuva
			
			#calcula o quanto choveu em cada dia
			daily_prec_sum = df_temp_hist.groupby(['Year', 'Month', df_temp_hist['Datetime'].dt.day])['prec'].sum().reset_index()
			
			#agora coloca uma flag falando que se choveu mais que 0.5 mm, esse é considerado um rainy day
			daily_prec_sum['RainyDay'] = (daily_prec_sum['prec'] > 1/1000).astype(int)
			
			#calcula o total de dias por mês
			total_days_per_month = daily_prec_sum.groupby(['Year', 'Month'])['RainyDay'].count().reset_index()
			total_days_per_month = total_days_per_month.rename(columns={'RainyDay': 'TotalDays'})

			#calcula a quantidade de dias que choveu em cada mes de cada ano		
			monthly_yearly_rainy_days = daily_prec_sum.groupby(['Year', 'Month'])['RainyDay'].sum().reset_index()

			#calcula a porcentagem de dias que choveu em cada dia e em cada ano
			percentage_rainy_days = pd.merge(monthly_yearly_rainy_days, total_days_per_month, on=['Year', 'Month'], how='left')
			percentage_rainy_days['PercentageRainyDays'] = (percentage_rainy_days['RainyDay'] / percentage_rainy_days['TotalDays']) * 100

			#faz a media mensal dos dias que choveu ao longo de todos os anos
			avg_percentage_rainy_days_monthly_hist = percentage_rainy_days.groupby('Month')['PercentageRainyDays'].mean().reset_index()

			monthly_prec_avg_hist = avg_percentage_rainy_days_monthly_hist['PercentageRainyDays']
		
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
		
		hours_tit = ':00 , '.join(['%1.0f' % val for val in selected_hours])
	else:
		monthly_temp_avg = df.groupby('Month')['temp'].mean()

	monthly_sst_avg = df_sst.groupby('Month')['sst'].mean()
	
	#PRECIPITAÇÃO - precisa somar todos os dados do mês - dados dão a precipitação a cada 3h - grafico é precipitação/mês
	
	# Agrupe os dados por ano e mês, somando a coluna 'prec' - o resultado é a precipitação total mensal ao longo dos anos
	monthly_prec_sum = df.groupby(['Year', 'Month'])['prec'].sum().reset_index()
	
	# Calcule a média mensal ao longo dos anos
	monthly_prec_avg = monthly_prec_sum.groupby('Month')['prec'].mean().reset_index()
	monthly_prec_avg = monthly_prec_avg['prec']*3000 #transformar para mm/mês (dado original está em m e em horas - dados a cada 3h (tranforma em 24 multiplicando por 3)
	
	
	if prec_kind == 'perc':	
		#precipitacao -- porcentagem de dias com chuva
		
		#calcula o quanto choveu em cada dia
		daily_prec_sum = df.groupby(['Year', 'Month', df['Datetime'].dt.day])['prec'].sum().reset_index()
		
		#agora coloca uma flag falando que se choveu mais que 0.5 mm, esse é considerado um rainy day
		daily_prec_sum['RainyDay'] = (daily_prec_sum['prec'] > 1/1000).astype(int)
		
		#calcula a quantidade de dias que choveu em cada mes de cada ano		
		monthly_yearly_rainy_days = daily_prec_sum.groupby(['Year', 'Month'])['RainyDay'].sum().reset_index()
		
		#calcula o total de dias por mês
		total_days_per_month = daily_prec_sum.groupby(['Year', 'Month'])['RainyDay'].count().reset_index()
		total_days_per_month = total_days_per_month.rename(columns={'RainyDay': 'TotalDays'})

		#calcula a porcentagem de dias que choveu em cada dia e em cada ano
		percentage_rainy_days = pd.merge(monthly_yearly_rainy_days, total_days_per_month, on=['Year', 'Month'], how='left')
		percentage_rainy_days['PercentageRainyDays'] = (percentage_rainy_days['RainyDay'] / percentage_rainy_days['TotalDays']) * 100

		#faz a media mensal dos dias que choveu ao longo de todos os anos
		avg_percentage_rainy_days_monthly = percentage_rainy_days.groupby('Month')['PercentageRainyDays'].mean().reset_index()
			
		monthly_prec_avg = avg_percentage_rainy_days_monthly['PercentageRainyDays']	
		
	
	
	
	
	month_names = ['Jan', 'Feb', 'Mar' , 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	if selected_years[0] == selected_years[-1]:
		title_years = f"{selected_years[0]}"
	else:
		title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	
	if selected_years != list(range(1993, 2025 + 1)):

		fig = make_subplots(rows=3, cols=1, shared_xaxes=False, vertical_spacing=0.05)
		
		# Adicione barras para precipitação primeiro
		trace_prec = go.Bar(
			x=month_names,
			#y=monthly_prec_avg['prec'],
			y=monthly_prec_avg,
			name='Precipitation (%s)'%title_years,
			marker=dict(color='rgba(64,183,173,1)')
		)
		
		# Adicione barras para precipitação primeiro
		trace_prec_hist = go.Bar(
			x=month_names,
			#y=monthly_prec_avg_hist['prec'],
			y=monthly_prec_avg_hist,
			name='Historic Precipitation (1993 to 2025)',
			marker=dict(color='rgba(0, 0, 0, 0.2)')
		)

		# Adicione os traços de linha
		trace_temp_hist = go.Scatter(
			x=month_names,
			y=monthly_temp_avg_hist,
			mode='lines',
			name='Historic Air Temp (%sh - 1993 to 2025)'%(hours_tit),
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
			name='Historic Sea Temp (1993 to 2025)',
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

		if prec_kind == 'perc':
			tit_y = f'Occurancy (%) of days with<br>precipitation over 1 mm/day'
		else:
			tit_y = 'Precipitation (mm/month)'
		

		fig.update_layout(
			title=dict(text=tit,font=dict(size=15)),
			yaxis=dict(title=tit_y),# range=[0, 200]),
			yaxis2=dict(title='Air Temp (°C)'),
			yaxis3=dict(title='Sea Temp (°C)'),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001,
			yaxis2_gridcolor='lightgray',
			yaxis2_gridwidth=0.0001,
			yaxis3_gridcolor='lightgray',
			yaxis3_gridwidth=0.0001,
			height=300*3,
			width=350,
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
			#y=monthly_prec_avg['prec'],
			y=monthly_prec_avg,
			name='Precipitation (%s)'%title_years,
			marker=dict(color='rgba(0, 0, 0, 0.2)')
		)
		
		trace_temp = go.Scatter(
			x=month_names,
			y=monthly_temp_avg,
			mode='lines+markers',
			name='Air Temp (%s:00 - %s)'%(hours_tit,title_years),
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
		
		if prec_kind == 'perc':
			tit_y = f'Occurancy (%) of days with<br>precipitation over 1 mm/day'
		else:
			tit_y = 'Precipitation (mm/month)'
		
		fig.update_layout(title=tit,
			yaxis=dict(title=tit_y),# range=[0, 200]),
			yaxis2=dict(
				title='Temp (°C)',
				overlaying='y',
				side='right',
				#range=[12, 32]
			),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001,
			height=300,
			width=350,
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
	


def plot_annual_stats_others(df_locais, df, selected_years, mes, parametro, nome_parametro, selected_location, selected_hours=None, prec_kind=None):

	tit = str(df_locais[df_locais['location'] == selected_location]['title'].values[0])
		
	years = list(selected_years)
	month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	title_month = f"{month_names[mes-1]}"
	
	if selected_hours is not None:
		df_selected_hours = df[df['Datetime'].dt.hour.isin(selected_hours)]
		month_data = df_selected_hours[df_selected_hours['Datetime'].dt.month == mes]
		hours_tit = ':00 , '.join(['%1.0f' % val for val in selected_hours])
		titul = '%s - %s (%s:00)'%(tit,title_month, hours_tit)
	else:
		month_data = df[df['Datetime'].dt.month == mes]
		titul = '%s - %s'%(tit,title_month)

	month_data['Year'] = month_data['Datetime'].dt.year
	month_data['Month'] = month_data['Datetime'].dt.month
	
	if parametro == 'prec': 
		monthly_prec_sum = month_data.groupby(['Year'])['prec'].sum().reset_index()
		montly_average_year = monthly_prec_sum['prec'] *3000 #transformar para mm/mês (dado original está em m e em horas - dados a cada 3h (tranforma em 24 multiplicando por 3)

		if prec_kind == 'perc':
			#calcula o quanto choveu em cada dia
			daily_prec_sum = month_data.groupby(['Year', 'Month', month_data['Datetime'].dt.day])['prec'].sum().reset_index()
			
			#agora coloca uma flag falando que se choveu mais que 0.5 mm, esse é considerado um rainy day
			daily_prec_sum['RainyDay'] = (daily_prec_sum['prec'] > 1/1000).astype(int)
			
			#calcula a quantidade de dias que choveu em cada mes de cada ano		
			monthly_yearly_rainy_days = daily_prec_sum.groupby(['Year', 'Month'])['RainyDay'].sum().reset_index()
			
			#calcula o total de dias por mês
			total_days_per_month = daily_prec_sum.groupby(['Year', 'Month'])['RainyDay'].count().reset_index()
			total_days_per_month = total_days_per_month.rename(columns={'RainyDay': 'TotalDays'})

			#calcula a porcentagem de dias que choveu em cada dia e em cada ano
			percentage_rainy_days = pd.merge(monthly_yearly_rainy_days, total_days_per_month, on=['Year', 'Month'], how='left')
			percentage_rainy_days['PercentageRainyDays'] = (percentage_rainy_days['RainyDay'] / percentage_rainy_days['TotalDays']) * 100

			monthly_prec_avg = percentage_rainy_days['PercentageRainyDays']	
		
			montly_average_year = monthly_prec_avg

	
	else:
		montly_average_year = month_data.groupby(['Year', month_data['Datetime'].dt.month])[parametro].mean()
		montly_average_year = montly_average_year.reset_index()
	
	fig = go.Figure()
	
	if parametro == 'prec':
		if prec_kind == 'perc':
			titulo = f'Occurancy (%) of days with<br>precipitation over 1 mm/day'
		else:
			titulo = 'Precipitation (mm/month)'
		trace = go.Bar(
			x=years,
			y=montly_average_year,
			name=nome_parametro,
			marker=dict(color='rgb(200, 200, 200)')
		)

	else:
		if parametro == 'temp': 
			line_color = 'rgb(67, 78, 150)'
			titulo = 'Air Temp (°C)'
		if parametro == 'sst': 
			line_color = 'rgb(220, 20, 60)'
			titulo = 'Sea Temp (°C)'
		
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
		title=dict(text=titul,font=dict(size=15)),
		yaxis=dict(title=titulo),
		plot_bgcolor='rgba(255,255,255,0)',
		yaxis_gridcolor='lightgray',
		yaxis_gridwidth=0.0001,
		height=300,
		width=350,
		margin=dict(l=10, r=10, t=40, b=10),
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

def wind_type(df,selected_location):
	
	onshore_str = df[df['location'] == selected_location]['onshore'].values[0]
	offshore_str = df[df['location'] == selected_location]['offshore'].values[0]
	side_str = df[df['location'] == selected_location]['side'].values[0]
	side_onshore_str = df[df['location'] == selected_location]['side_onshore'].values[0]
	side_offshore_str = df[df['location'] == selected_location]['side_offshore'].values[0]

	onshore = onshore_str.split(';')
	offshore = offshore_str.split(';')
	side = side_str.split(';')
	side_onshore = side_onshore_str.split(';')
	side_offshore = side_offshore_str.split(';')
	
	return onshore, offshore, side, side_onshore, side_offshore
	
# Função para converter os horários de acordo com o GMT específico
def converter_horarios_gmt(horarios, gmt):
	horarios_convertidos = [(hora + gmt) % 24 for hora in horarios]
	return horarios_convertidos
	
# def plot_map(df):
	# fig = go.Figure(
			# data=go.Scattergeo(
				# lat = df['lat'],
				# lon = df['lon'],
				# text = df['menu'].astype(str),
				# marker = dict(
					# color = 'red',
					# size = 10
				# )
			# )
	# )

	# fig.update_geos(#projection_type="orthographic",
		# resolution=50,
		# showcoastlines=True, coastlinecolor="Black", coastlinewidth=0.5,
		# showland=True, landcolor="rgb(212, 212, 212)", countrywidth=0.5,
		# #showocean=True, oceancolor="rgb(255, 255, 255)",
		# showcountries = True, countrycolor = "rgb(255, 255, 255)",
		# lonaxis = dict(
			# showgrid = True,
			# gridwidth = 0.5,
			# dtick=10
		# ),
		# lataxis = dict (
			# showgrid = True,
			# gridwidth = 0.5,
			# dtick=10
		# )		
	# )

	# fig.update_layout(
		# height=300, 
		# margin={"r":0,"t":0,"l":0,"b":0},
	# )
	# return fig


def plot_map(df):
	fig = px.scatter_mapbox(
		df,
		lat="lat",
		lon="lon",
		#text="menu",
		zoom=-0.55,
		mapbox_style="open-street-map",
		height=230,
		width=350,
		hover_name="menu",  # Set the column for hover information
		hover_data={"lat": False, "lon": False}  # Hide lat and lon in hover tooltip
	)

	fig.update_layout(
		mapbox=dict(
			center=dict(lat=0, lon=0),
			style="open-street-map"
		),
		margin=dict(r=0, t=0, l=0, b=0),
    )

	return fig





def plot_wind_hours(df_locais, df, selected_years, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, mes=None):

	tit = str(df_locais[df_locais['location'] == selected_location]['title'].values[0])
	
	if selected_years[0] == selected_years[-1]:
		title_years = f"{selected_years[0]}"
	else:
		title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	if mes is not None:
		df = df[df['Datetime'].dt.month == mes]
		month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		title_month = f"{month_names[mes-1]}"
		titul = f'{tit}<br>{nome_parametro} - {title_month} ({title_years})'
	else:
		titul = f'{tit}<br>{nome_parametro} - {title_years}'
	
	if parametro == 'CardinalDirection' or parametro == 'WindType':
		df['Range'] = pd.Categorical(df[parametro], categories=bins, ordered=True)
	else:
		df['Range'] = pd.cut(df[parametro], bins=bins, labels=labels, right=False)

	height_distribution = df.groupby([df['Datetime'].dt.hour, 'Range'])[parametro].count().unstack()
		
	
	
	# Calculando a porcentagem da distribuição
	height_distribution_percentage = height_distribution.div(height_distribution.sum(axis=1), axis=0) * 100
	
	# Obtendo os nomes dos meses
	hours_loc = sorted(df['Datetime'].dt.hour.unique())

	# Criando o gráfico de barras empilhadas com Plotly
	
	traces = []
	for col in height_distribution_percentage.columns:
		trace = go.Bar(
			x=hours_loc,
			y=height_distribution_percentage[col],
			name=f'{col}',
			marker=dict(color=bin_color_map[col])
		)
		traces.append(trace)

	if parametro=='CardinalDirection':
		layout = go.Layout(
			showlegend=False,
			title=dict(text=titul,font=dict(size=15)),
			yaxis=dict(title='Occurency (%)', range=[0, 100]),
			barmode='stack',
			height=330,
			width=350,
			margin=dict(l=10, r=10, t=80, b=10),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001
		)
	else:
		layout = go.Layout(
			title=dict(text=titul,font=dict(size=15)),
			yaxis=dict(title='Occurency (%)', range=[0, 100]),
			legend=dict(
				x=-0.15,
				y=-0.15,
				orientation='h',
				title='',
				font=dict(size=10)
			),
			barmode='stack',
			height=380,
			width=350,
			margin=dict(l=10, r=10, t=80, b=10),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001
		)

	hours_ticks = [f'{hour:02d}:00' for hour in hours_loc]
	layout.update(xaxis=dict(tickvals=hours_loc, ticktext=hours_ticks))

	fig = go.Figure(data=traces, layout=layout)
	
	return fig
	
	
def plot_others_hour(df_locais, df, selected_years, selected_location, mes, prec_kind):

	tit = str(df_locais[df_locais['location'] == selected_location]['title'].values[0])
	
	if selected_years[0] == selected_years[-1]:
		title_years = f"{selected_years[0]}"
	else:
		title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	df = df[df['Datetime'].dt.month == mes]
	month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	title_month = f"{month_names[mes-1]}"
	tit = f'{tit} - {title_month}'

	if selected_years != list(range(1993, 2025 + 1)):
		#####
		#historic data
		#####
		df_temp_hist = load_data(selected_location, list(range(1993, 2025 + 1)), 'VENTOS', df_locais)
		
		df_temp_hist = df_temp_hist[df_temp_hist['Datetime'].dt.month == mes]
		
		df_temp_hist['Hour'] = df_temp_hist['Datetime'].dt.hour
		
		hourly_temp_avg_hist = df_temp_hist.groupby('Hour')['temp'].mean()
		hourly_temp_std_hist = df_temp_hist.groupby('Hour')['temp'].std()

		hourly_prec_avg_hist = df_temp_hist.groupby('Hour')['prec'].mean()*1000
		hourly_prec_std_hist = df_temp_hist.groupby('Hour')['prec'].std()*1000
		
		if prec_kind == 'perc':
			#porcentagem de dias com mais de 0.1 mm/h
			df_temp_hist['RainyHour'] = (df_temp_hist['prec'] > .1/1000).astype(int)
			monthly_hourly_rainy = df_temp_hist.groupby(['Hour'])['RainyHour'].sum().reset_index()
			
			total_days_per_month = df_temp_hist.groupby(['Hour'])['RainyHour'].count().reset_index()
			total_days_per_month = total_days_per_month.rename(columns={'RainyHour': 'TotalDays'})
			
			#calcula a porcentagem de dias que choveu em cada dia e em cada ano
			percentage_rainy_days = pd.merge(monthly_hourly_rainy, total_days_per_month, on=['Hour'], how='left')
			
			percentage_rainy_days['PercentageRainyDays'] = (percentage_rainy_days['RainyHour'] / percentage_rainy_days['TotalDays']) * 100

			hourly_prec_avg_hist = percentage_rainy_days['PercentageRainyDays']	

		#####
		#####
		#####
		
		
	hours_loc = sorted(df['Datetime'].dt.hour.unique())
	
	df['Hour'] = df['Datetime'].dt.hour
		
	hourly_temp_avg = df.groupby('Hour')['temp'].mean()
	hourly_temp_std = df.groupby('Hour')['temp'].std()

	hourly_prec_avg = df.groupby('Hour')['prec'].mean()*1000
	hourly_prec_std = df.groupby('Hour')['prec'].std()*1000
	
	
	if prec_kind == 'perc':
		#porcentagem de dias com mais de 0.1 mm/h
		df['RainyHour'] = (df['prec'] > .1/1000).astype(int)
		monthly_hourly_rainy = df.groupby(['Hour'])['RainyHour'].sum().reset_index()
		
		total_days_per_month = df.groupby(['Hour'])['RainyHour'].count().reset_index()
		total_days_per_month = total_days_per_month.rename(columns={'RainyHour': 'TotalDays'})
		
		#calcula a porcentagem de dias que choveu em cada dia e em cada ano
		percentage_rainy_days = pd.merge(monthly_hourly_rainy, total_days_per_month, on=['Hour'], how='left')
		
		percentage_rainy_days['PercentageRainyDays'] = (percentage_rainy_days['RainyHour'] / percentage_rainy_days['TotalDays']) * 100

		hourly_prec_avg = percentage_rainy_days['PercentageRainyDays']	
	
		
	if selected_years[0] == selected_years[-1]:
		title_years = f"{selected_years[0]}"
	else:
		title_years = f"{selected_years[0]} to {selected_years[-1]}"
	
	
	if selected_years != list(range(1993, 2025 + 1)):

		fig = make_subplots(rows=2, cols=1, shared_xaxes=False, vertical_spacing=0.15)
		
		# Adicione barras para precipitação primeiro
		trace_prec = go.Bar(
			x=hours_loc,
			y=hourly_prec_avg,
			name='Precipitation (%s)'%title_years,
			marker=dict(color='rgba(64,183,173,1)')
		)
		
		# Adicione barras para precipitação primeiro
		trace_prec_hist = go.Bar(
			x=hours_loc,
			y=hourly_prec_avg_hist,
			name='Historic Precipitation (1993 to 2025)',
			marker=dict(color='rgba(0, 0, 0, 0.2)')
		)

		# Adicione os traços de linha
		trace_temp_hist = go.Scatter(
			x=hours_loc,
			y=hourly_temp_avg_hist,
			mode='lines',
			name='Historic Air Temp (1993 to 2025)',
			line=dict(color='rgb(67, 78, 150)', dash='dot'),
			
		)
		
		upper_bound = [avg + std for avg, std in zip(hourly_temp_avg_hist, hourly_temp_std_hist)]
		lower_bound = [avg - std for avg, std in zip(hourly_temp_avg_hist, hourly_temp_std_hist)]

		
		trace_temp_area = go.Scatter(
			x=hours_loc + hours_loc[::-1],  # Concatenate hours_loc with its reverse
			y=upper_bound + lower_bound[::-1],
			fill='toself',  # Indicates to fill the area
			fillcolor='rgba(67, 78, 150, 0.2)',  # Color and transparency of the filled area
			line=dict(color='rgba(255, 255, 255, 0)'),  # Hide the line of the area trace
			showlegend=False,  # Do not show legend for the area trace
			
		)
		
		trace_temp = go.Scatter(
			x=hours_loc,
			y=hourly_temp_avg,
			mode='lines+markers',
			name='Air Temp (%s)'%(title_years),
			line=dict(color='rgb(67, 78, 150)'),
			
		)

		if prec_kind == 'perc':
			tit_y = f'Occurancy (%) of days with<br>precipitation over 0.1 mm/h'
		else:
			tit_y = 'Precipitation (mm/h)'
		
		fig.update_layout(
			title=dict(text=tit,font=dict(size=15)),
			yaxis=dict(title=tit_y),# range=[0, 200]),
			yaxis2=dict(title='Air Temp (°C)'),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001,
			yaxis2_gridcolor='lightgray',
			yaxis2_gridwidth=0.0001,
			height=200*3,
			width=350,
			margin=dict(l=10, r=10, t=60, b=10),
			legend=dict(
				x=-0.15,
				y=-0.1,
				orientation='h',
				bgcolor='rgba(255, 255, 255, 0)',
				traceorder='normal',  # Ordem padrão de exibição dos itens da legenda
				bordercolor='rgba(255, 255, 255, 0)',  # Cor da borda da legenda (transparente)
				borderwidth=0,  # Largura da borda da legenda
				xanchor='left',  # Ancoragem horizontal no centro
				yanchor='top'  # Ancoragem vertical no topo
			)
		)
		
		hours_ticks = [f'{hour:02d}:00' for hour in hours_loc]
		fig.update_layout(xaxis=dict(tickvals=hours_loc, ticktext=hours_ticks))
		fig.update_layout(xaxis2=dict(tickvals=hours_loc, ticktext=hours_ticks))
		
		fig.add_trace(trace_prec_hist, row=1, col=1)
		fig.add_trace(trace_prec, row=1, col=1)
		fig.add_trace(trace_temp_area, row=2, col=1)
		fig.add_trace(trace_temp_hist, row=2, col=1)
		fig.add_trace(trace_temp, row=2, col=1)
		
	else:
		fig = go.Figure()
		
		trace_prec = go.Bar(
			x=hours_loc,
			y=hourly_prec_avg,
			name='Precipitation (%s)'%title_years,
			marker=dict(color='rgba(0, 0, 0, 0.2)')
		)
		
		trace_temp = go.Scatter(
			x=hours_loc,
			y=hourly_temp_avg,
			mode='lines+markers',
			name='Air Temp (%s)'%(title_years),
			line=dict(color='rgb(67, 78, 150)'),
			yaxis='y2'
		)

		if prec_kind == 'perc':
			tit_y = f'Occurancy (%) of days with<br>precipitation over 0.1 mm/h'
		else:
			tit_y = 'Precipitation (mm/h)'

		fig.update_layout(title=dict(text=tit,font=dict(size=15)),
			yaxis=dict(title=tit_y),# range=[0, 200]),
			yaxis2=dict(
				title='Temp (°C)',
				overlaying='y',
				side='right',
				#range=[12, 32]
			),
			plot_bgcolor='rgba(255,255,255,0)',
			yaxis_gridcolor='lightgray',
			yaxis_gridwidth=0.0001,
			height=300,
			width=350,
			margin=dict(l=10, r=10, t=60, b=10),
			legend=dict(
				x=0,
				y=-0.25,
				orientation='h',
				bgcolor='rgba(255, 255, 255, 0)',
				traceorder='normal',  # Ordem padrão de exibição dos itens da legenda
				bordercolor='rgba(255, 255, 255, 0)',  # Cor da borda da legenda (transparente)
				borderwidth=0,  # Largura da borda da legenda
				xanchor='left',  # Ancoragem horizontal no centro
				yanchor='top'  # Ancoragem vertical no topo
			)
		)
		
		hours_ticks = [f'{hour:02d}:00' for hour in hours_loc]
		fig.update_layout(xaxis=dict(tickvals=hours_loc, ticktext=hours_ticks))
		fig.update_layout(xaxis2=dict(tickvals=hours_loc, ticktext=hours_ticks))
	
		fig.add_trace(trace_prec)
		fig.add_trace(trace_temp)
			
	return fig