df_locais = pd.read_csv('locais.csv');
fig_map = plot_map(df_locais)

rose = plot_rose()


# Callbacks para atualizar os gráficos e a guia ativa
@app.callback(
	[Output('monthly-stats-plot-alt', 'figure'),
	 Output('monthly-stats-plot-dir', 'figure'),
	 Output('rose_wind1', 'figure'),
	 Output('monthly-stats-plot-per', 'figure'),
	 Output('custom-conditions-plot', 'figure'),
	 Output('annual-stats-plot-alt', 'figure'),
	 Output('annual-stats-plot-dir', 'figure'),
	 Output('rose_wind2', 'figure'),
	 Output('annual-stats-plot-per', 'figure'),
	 Output('monthly-stats-plot-int_wind', 'figure'),
	 Output('monthly-stats-plot-dir_wind', 'figure'),
	 Output('rose_wind3', 'figure'),
	 Output('monthly-stats-plot-dir_wind_t', 'figure'),
	 Output('annual-stats-plot-int_wind', 'figure'),
	 Output('annual-stats-plot-dir_wind', 'figure'),
	 Output('rose_wind4', 'figure'),
	 Output('annual-stats-plot-dir_wind_t', 'figure'),
	 Output('hour-month-plot-int_wind', 'figure'),
	 Output('hour-month-plot-dir_wind', 'figure'),
	 Output('rose_wind4a', 'figure'),
	 Output('hour-month-plot-dir_wind_t', 'figure'),
	 Output('other_anual_times', 'figure'),
	 Output('other_times', 'figure'),
	 Output('annual-stats-plot-prec', 'figure'),
	 Output('annual-stats-plot-temp', 'figure'),
	 Output('annual-stats-plot-sst', 'figure'),
	 Output('tabs', 'active_tab'),
	 Output('waves-content', 'style'),
	 Output('wind-content', 'style'),
	 Output('others-content', 'style'),
	 Output('map', 'figure'),
	 Output('update-button', 'n_clicks')],
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
	 Input('tabs', 'active_tab'),
	 Input('horarios-checklist_wind', 'value'),
	 Input('horarios-checklist_sst', 'value'),
	 Input('month-dropdown_others', 'value')]
)
def update_plots(n_clicks,  selected_location, start_year, end_year, selected_month, selected_month_wind, altura1, periodo1, direcao1, altura2, periodo2, direcao2, altura3, periodo3, direcao3, active_tab, selected_hours, selected_hours_others, selected_month_others):

	button_clicked = ctx.triggered_id
	
	if button_clicked:
		# Check if the button was clicked
		#if n_clicks == 0:
		#	raise PreventUpdate

		anos = list(range(start_year, end_year + 1))

		if active_tab == "waves":
		
			df = load_data(selected_location, anos, 'ONDAS', df_locais)
			
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

			fig1 = plot_monthly_stats(df_locais, df, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location)
			fig4 = plot_annual_stats(df_locais, df, anos, selected_month, bins, labels, parametro, nome_parametro, bin_color_map, selected_location)

			bins = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
			labels = bins
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

			fig2 = plot_monthly_stats(df_locais, df, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location)
			fig5 = plot_annual_stats(df_locais, df, anos, selected_month, bins, labels, parametro, nome_parametro, bin_color_map, selected_location)

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

			fig3 = plot_monthly_stats(df_locais, df, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location)
			fig6 = plot_annual_stats(df_locais, df, anos, selected_month, bins, labels, parametro, nome_parametro, bin_color_map, selected_location)

			conditions = [{'altura': altura1, 'periodo': periodo1, 'direcao': direcao1},
			{'altura': altura2, 'periodo': periodo2, 'direcao': direcao2},
			{'altura': altura3, 'periodo': periodo3, 'direcao': direcao3}]
			
			fig_custom_conditions = plot_custom_conditions_frequency(df, conditions, anos)

			return [fig1, fig2, rose, fig3, fig_custom_conditions, fig4, fig5, rose, fig6] + [no_update]*12 + [no_update]*5 + [active_tab, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}, fig_map, 0]

		elif active_tab == "wind":
		
			df_wind = load_data(selected_location, anos, 'VENTOS', df_locais)
			
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

			fig1_w = plot_monthly_stats(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours)
			fig4_w = plot_annual_stats(df_locais, df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours)
			#fig6_w = plot_wind_hours(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location);
			fig6a_w = plot_wind_hours(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_month_wind);
			
			bins = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
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
			
			fig2a_w = plot_monthly_stats(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours)
			fig5a_w = plot_annual_stats(df_locais, df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro,bin_color_map, selected_location, selected_hours)
			#fig7_w = plot_wind_hours(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location);
			fig7a_w = plot_wind_hours(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_month_wind);
			
			onshore, offshore, side, side_onshore, side_offshore = wind_type(df_locais,selected_location);

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
			
			fig2_w = plot_monthly_stats(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours)
			fig5_w = plot_annual_stats(df_locais, df_wind, anos, selected_month_wind, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_hours)
			#fig8_w = plot_wind_hours(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location);
			fig8a_w = plot_wind_hours(df_locais, df_wind, anos, bins, labels, parametro, nome_parametro, bin_color_map, selected_location, selected_month_wind);
			
			return [no_update]*9 + [fig1_w, fig2a_w, rose, fig2_w, fig4_w, fig5a_w, rose, fig5_w, fig6a_w, fig7a_w, rose, fig8a_w] + [no_update]*5 + [active_tab, {'display': 'none'}, {'display': 'block'}, {'display': 'none'}, fig_map,0]

		elif active_tab == "other":
		
			df_wind = load_data(selected_location, anos, 'VENTOS', df_locais)
			df_sst = load_data(selected_location, anos, 'SST', df_locais)
				
			fig_other = plot_others(df_locais, df_wind, df_sst, anos, selected_location, selected_hours_others)
			fig_other_prec = plot_annual_stats_others(df_locais, df_wind, anos, selected_month_others, 'prec', 'Precipitation', selected_location)
			fig_other_temp = plot_annual_stats_others(df_locais, df_wind, anos, selected_month_others, 'temp', 'Air Temp', selected_location, selected_hours_others)
			fig_other_sst = plot_annual_stats_others(df_locais, df_sst, anos, selected_month_others, 'sst', 'Sea Temp', selected_location)
			fig_other_hourly = plot_others_hour(df_locais, df_wind, anos, selected_location, selected_month_others)
			
			return [no_update]*9 + [no_update]*12 + [fig_other, fig_other_hourly, fig_other_prec, fig_other_temp, fig_other_sst] + [active_tab, {'display': 'none'}, {'display': 'none'}, {'display': 'block'}, fig_map, 0]

	else:
		return [no_update]*9 + [no_update]*12 + [no_update]*5 + [active_tab, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, fig_map, 0]
	
# Callback para atualizar dinamicamente os rótulos dos horários para hora local
@app.callback(
	[Output('horarios-checklist_wind', 'options'),
	Output('horarios-checklist_wind', 'value'),
	Output('horarios-checklist_sst', 'options'),
	Output('horarios-checklist_sst', 'value'),],
	[Input('location-dropdown', 'value')]
	)
def update_horarios_labels(selected_location):
	horario_original = [0, 3, 6, 9, 12, 15, 18, 21];
	horario_gmt = df_locais[df_locais['location'] == selected_location]['time_zone'].values
	
	horarios_convertidos = sorted(converter_horarios_gmt(horario_original, horario_gmt))
	
	closest = min(horarios_convertidos, key=lambda x: abs(x[0] - 9))
	
	horarios_atualizados = [{'label': f' {hora[0]:02d}:00   ', 'value': hora[0]} for hora in horarios_convertidos]

	return  horarios_atualizados, [closest[0]], horarios_atualizados, [closest[0]]