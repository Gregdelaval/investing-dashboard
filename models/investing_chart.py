from .base_models import BaseModels
from ..helpers.helpers import Helpers
from ..helpers.data_provider import DataProvier
from bokeh import models, events
import pandas


class InvestingChart(BaseModels, DataProvier):
	granularities = {
		'1m': {
		'format': '%Y-%m-%d %H:%M'
		},
		'5m': {
		'format': '%Y-%m-%d %H:%M'
		},
		'15m': {
		'format': '%Y-%m-%d %H:%M'
		},
		'1h': {
		'format': '%Y-%m-%d %H'
		},
		'1d': {
		'format': '%Y-%m-%d'
		},
		'1wk': {
		'format': '%Y-%m-%d'
		},
		'1mo': {
		'format': '%Y-%m'
		},
		'3mo': {
		'format': '%Y-%m'
		},
	}
	data_display_types = ['Candle', 'Line', 'Bar']

	def __init__(
		self,
		chart_width: int,
		chart_height: int,
	) -> None:
		super().__init__()
		#Set chart dimensions
		self.chart_width = chart_width
		self.chart_height = chart_height

		#define labels
		self.primary_axis_header = self.divider(text='Primary figure')
		self.primary_axis_portfolio_descriptor = self.pretext(text='Show investments')
		self.secondary_axis_header = self.divider(text='Secondary figure')

		#Data set controllers
		symbols_mapping = self.fetch_symbols_mapping()
		self.trigger_calculation_button = self.button(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			self.set_default_view_ranges,
			label='Update',
		)
		self.primary_instrument_selector = self.selector(
			title='Instrument',
			options=symbols_mapping['common_name'].values.tolist(),
		)
		self.primary_granularity_selector = self.selector(
			options=list(self.granularities.keys()),
			title='Granularity',
			sort=False,
		)
		self.secondary_instrument_selector = self.selector(
			title='Instrument',
			options=symbols_mapping['common_name'].values.tolist(),
		)
		self.secondary_granularity_selector = self.selector(
			options=list(self.granularities.keys()),
			title='Granularity',
			sort=False,
		)
		self.set_data_set()
		#Primary glyph controllers
		self.primary_display_type_selector = self.selector(
			self.set_controllers,
			title='Display Type',
			options=self.data_display_types,
			sort=False,
		)
		self.primary_line_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Line based on field',
		)
		self.primary_ohlc_o_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Open',
			value='open',
		)
		self.primary_ohlc_h_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='High',
			value='high',
		)
		self.primary_ohlc_l_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Low',
			value='low',
		)
		self.primary_ohlc_c_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Close',
			value='close',
		)
		self.primary_bar_top_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Top',
			value='volume',
		)
		self.primary_bar_bottom_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Bottom',
			value=0,
		)
		self.portfolio_open_positions_toggle = self.define_toggle(label='Open Positions',)
		self.portfolio_historical_positions_toggle = self.define_toggle(label='Historical Positions',)
		#Secondary glyph controllers
		self.secondary_display_type_selector = self.selector(
			self.set_controllers,
			title='Display Type',
			options=self.data_display_types,
			sort=False,
		)
		self.secondary_line_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='Line based on field',
		)
		self.secondary_ohlc_o_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='Open',
			value='open',
		)
		self.secondary_ohlc_h_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='High',
			value='high',
		)
		self.secondary_ohlc_l_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='Low',
			value='low',
		)
		self.secondary_ohlc_c_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='Close',
			value='close',
		)
		self.secondary_bar_top_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='Top',
			value='volume',
		)
		self.secondary_bar_bottom_field_selector = self.selector(
			options=self.secondary_figure_data_set.columns.tolist(),
			title='Bottom',
			value=0,
		)

		#Glyphs
		self._background_label = self.label(
			text_alpha=0.1,
			text_font_size='32px',
			text_align='center',
			x_units='screen',
			y_units='screen',
			x=self.chart_width * 0.5,
			y=self.chart_height * 0.65,
		)
		self._primary_vbar = self.define_vbar(
			x='index',
			top='volume',
			bottom=0,
			fill_color='color',
			width=0.5,
		)
		self._primary_figure_line = self.define_line(
			x='index',
			y='close',
		)
		self._primary_axis_ohlc_candle_line = self.define_segment(
			x0='index',
			y0='high',
			x1='index',
			y1='low',
			line_color='black',
		)
		self._primary_axis_ohlc_candle_bar = self.define_vbar(
			x='index',
			top='open',
			bottom='close',
			fill_color='color',
			width=0.5,
		)
		self._secondary_vbar = self.define_vbar(
			x='position',
			top='volume',
			bottom=0,
			fill_color='color',
			width=0.5,
		)
		self._secondary_figure_line = self.define_line(
			x='position',
			y='close',
		)
		self._secondary_axis_ohlc_candle_line = self.define_segment(
			x0='position',
			y0='high',
			x1='position',
			y1='low',
			line_color='black',
		)
		self._secondary_axis_ohlc_candle_bar = self.define_vbar(
			x='position',
			top='open',
			bottom='close',
			fill_color='color',
			width=0.5,
		)
		self._historical_close_positions_glyph = self.define_scatter(
			x='close_position',
			y='close_rate',
			marker='circle',
			fill_color='closing_color',
			fill_alpha=0.5,
			line_alpha=0,
		)
		self._historical_open_positions_glyph = self.define_scatter(
			x='open_position', y='open_rate', marker='marker', fill_color='gray'
		)
		self._historical_position_connector_glyph = self.define_segment(
			x0='open_position',
			y0='open_rate',
			x1='close_position',
			y1='close_rate',
			line_color='closing_color',
			line_alpha=0.5,
		)
		self._open_positions_glyph = self.define_scatter(
			x='position',
			y='open_rate',
			marker='marker',
			fill_color='turquoise',
		)
		self._stop_loss_vline_glyph = self.define_segment(
			x0='position',
			y0='open_rate',
			x1='position',
			y1='stop_loss_rate',
			line_color='red',
			line_alpha=0.5,
		)
		self._stop_loss_hline_glyph = self.define_segment(
			x0='position_neg_offset',
			y0='stop_loss_rate',
			x1='position_pos_offset',
			y1='stop_loss_rate',
			line_color='red',
			line_alpha=0.9,
		)
		self._take_profit_vline_glyph = self.define_segment(
			x0='position',
			y0='open_rate',
			x1='position',
			y1='take_profit_rate',
			line_color='green',
			line_alpha=0.5,
		)
		self._take_profit_hline_glyph = self.define_segment(
			x0='position_neg_offset',
			y0='take_profit_rate',
			x1='position_pos_offset',
			y1='take_profit_rate',
			line_color='green',
			line_alpha=0.9,
		)

		#Invoke model event handlers
		self.set_data_view()
		self.set_source()
		self.set_controllers()

		#Define figure
		#TODO overlay showing leverage distances
		#TODO add option to overlay and normalize charts
		#TODO add event handler to base models figure definition
		self.primary_figure = self.define_figure(
			x_axis_type='datetime',
			active_scroll='wheel_zoom',
			width=self.chart_width,
			height=int((7 * self.chart_height) / 9),
			y_range=(
			self.primary_figure_data_view['close'].min(), self.primary_figure_data_view['close'].max()
			),
			x_range=(0, self.primary_figure_data_view.index.max()),
		)
		self.primary_figure.yaxis.ticker.desired_num_ticks = 25
		self.primary_figure.xaxis.ticker.desired_num_ticks = 10
		self.primary_figure.yaxis.formatter = models.NumeralTickFormatter(format='0')
		width = models.Span(dimension="width")
		height = models.Span(dimension="height")
		self.primary_figure.add_glyph(self._primary_source, self._primary_figure_line)
		self.primary_figure.add_glyph(self._primary_source, self._primary_vbar)
		self.primary_figure.add_glyph(self._primary_source, self._primary_axis_ohlc_candle_line)
		candle_bar_renderer = self.primary_figure.add_glyph(self._primary_source, self._primary_axis_ohlc_candle_bar) # yapf: disable
		self.primary_figure.add_glyph(self._historical_positions_source, self._historical_position_connector_glyph)  # yapf: disable
		self.primary_figure.add_glyph(self._historical_positions_source, self._historical_open_positions_glyph)# yapf: disable
		self.primary_figure.add_glyph(self._historical_positions_source, self._historical_close_positions_glyph) # yapf: disable
		self.primary_figure.add_glyph(self._open_positions_source, self._open_positions_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._stop_loss_vline_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._stop_loss_hline_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._take_profit_hline_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._take_profit_vline_glyph)
		self.primary_figure.add_layout(self._background_label, 'center')
		#TODO add options to choose tool configuration on runtime (example, for portfolio overlay)
		hover = self.define_hover_tool(
			tooltips=[
			('Date', '@datetime{%Y-%m-%d %H:%M:%S}'),
			('Change', '@change{0.0f} %'),
			('Open', '@open{,0.00}'),
			('High', '@high{,0.00}'),
			('Low', '@low{,0.00}'),
			('Close', '@close{,0.00}'),
			],
			formatters={'@datetime': 'datetime'},
			renderers=[candle_bar_renderer],
		)
		self.primary_figure.add_tools(
			hover,
			models.PanTool(),
			models.WheelZoomTool(dimensions='width', speed=1 / 900),
			models.CrosshairTool(overlay=[width, height]),
		)
		self.primary_figure.on_event(events.MouseWheel, self.set_preferred_view_ranges)

		self.secondary_figure = self.define_figure(
			x_axis_type=None,
			active_scroll='wheel_zoom',
			width=self.chart_width,
			height=int((2 * self.chart_height) / 9),
			y_range=(
			self.secondary_figure_data_view['close'].min(), self.secondary_figure_data_view['close'].max()
			),
			x_range=self.primary_figure.x_range,
		)
		self.secondary_figure.yaxis.formatter = models.NumeralTickFormatter(format='0')
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_figure_line)
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_vbar)
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_axis_ohlc_candle_line)
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_axis_ohlc_candle_bar)
		self.secondary_figure.add_tools(
			models.PanTool(),
			models.WheelZoomTool(dimensions='width', speed=1 / 900),
			models.CrosshairTool(overlay=[width, height]),
		)

		#Invoke view event handlers
		self.set_glyphs()
		self.set_default_view_ranges()

	def set_controllers(self) -> None:
		self.primary_line_field_selector.options = self.primary_figure_data_view.columns.tolist()
		self.secondary_line_field_selector.options = self.secondary_figure_data_view.columns.tolist()

		#TODO Figure out how to only call the previous value (identify caller?)
		self.primary_line_field_selector.visible = False
		self.primary_ohlc_o_field_selector.visible = False
		self.primary_ohlc_h_field_selector.visible = False
		self.primary_ohlc_l_field_selector.visible = False
		self.primary_ohlc_c_field_selector.visible = False
		self.primary_bar_bottom_field_selector.visible = False
		self.primary_bar_top_field_selector.visible = False
		self.secondary_line_field_selector.visible = False
		self.secondary_ohlc_o_field_selector.visible = False
		self.secondary_ohlc_h_field_selector.visible = False
		self.secondary_ohlc_l_field_selector.visible = False
		self.secondary_ohlc_c_field_selector.visible = False
		self.secondary_bar_bottom_field_selector.visible = False
		self.secondary_bar_top_field_selector.visible = False
		if self.primary_display_type_selector.value == 'Line':
			self.primary_line_field_selector.visible = True
		if self.primary_display_type_selector.value == 'Candle':
			self.primary_ohlc_o_field_selector.visible = True
			self.primary_ohlc_h_field_selector.visible = True
			self.primary_ohlc_l_field_selector.visible = True
			self.primary_ohlc_c_field_selector.visible = True
		if self.primary_display_type_selector.value == 'Bar':
			self.primary_bar_bottom_field_selector.visible = True
			self.primary_bar_top_field_selector.visible = True
		if self.secondary_display_type_selector.value == 'Line':
			self.secondary_line_field_selector.visible = True
		if self.secondary_display_type_selector.value == 'Candle':
			self.secondary_ohlc_o_field_selector.visible = True
			self.secondary_ohlc_h_field_selector.visible = True
			self.secondary_ohlc_l_field_selector.visible = True
			self.secondary_ohlc_c_field_selector.visible = True
		if self.secondary_display_type_selector.value == 'Bar':
			self.secondary_bar_bottom_field_selector.visible = True
			self.secondary_bar_top_field_selector.visible = True

	def set_glyphs(self) -> None:
		self._background_label.update(
			text=f'{self.primary_instrument_selector.value} - {self.primary_granularity_selector.value}'
		)
		self.primary_figure.xaxis.major_label_overrides = self.primary_figure_data_view[
			'datetime'].dt.strftime(self.granularities[self.primary_granularity_selector.value]['format']).to_dict() # yapf: disable
		#Hide everything by default
		self._primary_axis_ohlc_candle_line.line_alpha = 0
		self._primary_axis_ohlc_candle_bar.line_alpha = 0
		self._primary_axis_ohlc_candle_bar.fill_alpha = 0
		self._primary_vbar.line_alpha = 0
		self._primary_vbar.fill_alpha = 0
		self._primary_figure_line.line_alpha = 0
		self._secondary_axis_ohlc_candle_line.line_alpha = 0
		self._secondary_axis_ohlc_candle_bar.line_alpha = 0
		self._secondary_axis_ohlc_candle_bar.fill_alpha = 0
		self._secondary_vbar.line_alpha = 0
		self._secondary_vbar.fill_alpha = 0
		self._secondary_figure_line.line_alpha = 0
		self._historical_open_positions_glyph.size = 0
		self._historical_close_positions_glyph.size = 0
		self._historical_position_connector_glyph.line_width = 0
		self._take_profit_vline_glyph.line_width = 0
		self._take_profit_hline_glyph.line_width = 0
		self._stop_loss_vline_glyph.line_width = 0
		self._stop_loss_hline_glyph.line_width = 0
		self._open_positions_glyph.size = 0
		if self.primary_display_type_selector.value == 'Line':
			self._primary_figure_line.line_alpha = 1
			self._primary_figure_line.y = self.primary_line_field_selector.value
		if self.primary_display_type_selector.value == 'Candle':
			self._primary_axis_ohlc_candle_line.line_alpha = 1
			self._primary_axis_ohlc_candle_bar.line_alpha = 1
			self._primary_axis_ohlc_candle_bar.fill_alpha = 1
		if self.primary_display_type_selector.value == 'Bar':
			self._primary_vbar.line_alpha = 1
			self._primary_vbar.fill_alpha = 1
		if self.secondary_display_type_selector.value == 'Line':
			self._secondary_figure_line.line_alpha = 1
			self._secondary_figure_line.y = self.secondary_line_field_selector.value
		if self.secondary_display_type_selector.value == 'Candle':
			self._secondary_axis_ohlc_candle_line.line_alpha = 1
			self._secondary_axis_ohlc_candle_bar.line_alpha = 1
			self._secondary_axis_ohlc_candle_bar.fill_alpha = 1
		if self.secondary_display_type_selector.value == 'Bar':
			self._secondary_vbar.line_alpha = 1
			self._secondary_vbar.fill_alpha = 1
		if self.portfolio_historical_positions_toggle.active:
			self._historical_open_positions_glyph.size = 10
			self._historical_close_positions_glyph.size = 8
			self._historical_position_connector_glyph.line_width = 0.3
		if self.portfolio_open_positions_toggle.active:
			self._open_positions_glyph.size = 10
			self._stop_loss_vline_glyph.line_width = 0.3
			self._stop_loss_hline_glyph.line_width = 0.7
			self._take_profit_hline_glyph.line_width = 0.7
			self._take_profit_vline_glyph.line_width = 0.3

	def set_data_set(self) -> None:
		self.primary_figure_data_set = self.fetch_investing_instrument(
			symbol=self.primary_instrument_selector.value,
			granularity=self.primary_granularity_selector.value,
		)
		self.secondary_figure_data_set = self.fetch_investing_instrument(
			symbol=self.secondary_instrument_selector.value,
			granularity=self.primary_granularity_selector.value,
		)
		self.open_positions_data_set = self.fetch_portfolio_open_positions()
		self.historical_positions_data_set = self.fetch_portfolio_historical_positions()

	def set_data_view(self) -> None:
		self.log.info('Calculating data view')
		#TODO fix datetime dtypes in portfolio prj
		###OHLC DATA VIEW###
		self.primary_figure_data_view = self.primary_figure_data_set
		#Order values by datetime
		self.primary_figure_data_view.sort_values(by='datetime', ascending=True, inplace=True)
		#Define change
		self.primary_figure_data_view['change'] = (
			self.primary_figure_data_view['close'] - self.primary_figure_data_view['close'].shift(1)
		) / self.primary_figure_data_view['close'].shift(1) * 100
		#Define bar color
		self.primary_figure_data_view['color'] = 'red'
		_green_mask = (self.primary_figure_data_view['open'] < self.primary_figure_data_view['close'])
		self.primary_figure_data_view.loc[_green_mask, 'color'] = 'green'
		# reset index
		self.primary_figure_data_view.reset_index(inplace=True, drop=True)

		###SECONDARY DATA VIEW###
		self.secondary_figure_data_view = self.secondary_figure_data_set
		#Order values by datetime
		self.secondary_figure_data_view.sort_values(by='datetime', ascending=True, inplace=True)
		#Define bar color
		self.secondary_figure_data_view['color'] = 'red'
		_green_mask = (self.secondary_figure_data_view['open'] < self.secondary_figure_data_view['close'])
		self.secondary_figure_data_view.loc[_green_mask, 'color'] = 'green'
		#Set index position
		self.secondary_figure_data_view['position'] = \
    self.secondary_figure_data_view['datetime'].apply(
			lambda x: Helpers().find_closest_neighbour(
			for_value=x,
			in_df=self.primary_figure_data_view,
			in_column='datetime',
			))

		###OPEN POSITIONS DATA VIEW###
		self.open_positions_view = self.open_positions_data_set
		self.open_positions_view['open_datetime'] = pandas.to_datetime(
			self.open_positions_view['open_datetime']
		)
		#Set index position
		self.open_positions_view['position'] = self.open_positions_view['open_datetime'].apply(
			lambda x: Helpers().find_closest_neighbour(
			for_value=x,
			in_df=self.primary_figure_data_view,
			in_column='datetime',
			)
		)
		self.open_positions_view = self.open_positions_view.loc[self.open_positions_view['common_name'] ==
			self.primary_instrument_selector.value]
		self.open_positions_view = self.open_positions_view.loc[self.open_positions_view['position'] != 0]
		self.open_positions_view['marker'] = 'triangle'
		self.open_positions_view.loc[self.open_positions_view['is_buy'] == 0,
			'marker'] = 'inverted_triangle'
		self.open_positions_view['position_neg_offset'] = self.open_positions_view['position'] - 1
		self.open_positions_view['position_pos_offset'] = self.open_positions_view['position'] + 1

		###HISTORICAL POSITIONS DATA VIEW###
		self.historical_positions_view = self.historical_positions_data_set
		self.historical_positions_view['open_datetime'] = pandas.to_datetime(
			self.historical_positions_view['open_datetime']
		)
		self.historical_positions_view['close_datetime'] = pandas.to_datetime(
			self.historical_positions_view['close_datetime']
		)
		self.historical_positions_view['open_position'] = self.historical_positions_view['open_datetime'].apply( # yapf: disable
			lambda x: Helpers().find_closest_neighbour(
			for_value=x,
			in_df=self.primary_figure_data_view,
			in_column='datetime',
			)
		)
		self.historical_positions_view['close_position'] = self.historical_positions_view['close_datetime'].apply( # yapf: disable
			lambda x: Helpers().find_closest_neighbour(
			for_value=x,
			in_df=self.primary_figure_data_view,
			in_column='datetime',
			)
		)
		self.historical_positions_view = self.historical_positions_view.loc[
			self.historical_positions_view['common_name'] == self.primary_instrument_selector.value]
		self.historical_positions_view = self.historical_positions_view.loc[
			self.historical_positions_view['open_position'] != 0]
		self.historical_positions_view['marker'] = 'triangle'
		self.historical_positions_view.loc[self.historical_positions_view['is_buy'] == 0,
			'marker'] = 'inverted_triangle'
		self.historical_positions_view['closing_color'] = 'red'
		_shorting_mask = (
			(self.historical_positions_view['open_rate'] > self.historical_positions_view['close_rate'])
			& (self.historical_positions_view['is_buy'] == 0)
		)
		_longing_mask = (
			(self.historical_positions_view['open_rate'] < self.historical_positions_view['close_rate'])
			& self.historical_positions_view['is_buy'] == 1
		)
		self.historical_positions_view.loc[(_shorting_mask | _longing_mask), 'closing_color'] = 'green'
		self.log.info('Calculated data view')

	def set_source(self) -> None:
		try:
			self._primary_source.data.update(self.column_data_source(self.primary_figure_data_view).data)
			self._secondary_source.data.update(self.column_data_source(self.secondary_figure_data_view).data)
			self._open_positions_source.data = self.open_positions_view.to_dict(orient='list')
			self._historical_positions_source.data = self.historical_positions_view.to_dict(orient='list')
		except AttributeError:
			self._primary_source = self.column_data_source(self.primary_figure_data_view)
			self._secondary_source = self.column_data_source(self.secondary_figure_data_view)
			self._open_positions_source = self.column_data_source(self.open_positions_view)
			self._historical_positions_source = self.column_data_source(self.historical_positions_view)

	def set_default_view_ranges(self) -> None:
		#X range defaults
		_x_range_preferred_min = self.primary_figure_data_view.index.max() - 180
		_x_range_preferred_max = self.primary_figure_data_view.index.max() + 5

		#Set X ranges
		self.primary_figure.x_range.start = _x_range_preferred_min
		self.primary_figure.x_range.end = _x_range_preferred_max
		self.secondary_figure.x_range.start = _x_range_preferred_min
		self.secondary_figure.x_range.end = _x_range_preferred_max

		#Fig 1 Y range defaults
		_mask = (self.primary_figure_data_view.index >=_x_range_preferred_min) & (self.primary_figure_data_view.index <= _x_range_preferred_max)#yapf: disable
		if self.primary_display_type_selector.value == 'Candle':
			_y_min = self.primary_figure_data_view.loc[_mask][self.primary_ohlc_l_field_selector.value].min() #yapf: disable
			_y_max = self.primary_figure_data_view.loc[_mask][self.primary_ohlc_h_field_selector.value].max() #yapf: disable
		if self.primary_display_type_selector.value == 'Line':
			_y_min = self.primary_figure_data_view.loc[_mask][self.primary_line_field_selector.value].min() #yapf: disable
			_y_max = self.primary_figure_data_view.loc[_mask][self.primary_line_field_selector.value].max() #yapf: disable
		if self.primary_display_type_selector.value == 'Bar':
			_y_min = self.primary_figure_data_view.loc[_mask][self.primary_bar_bottom_field_selector.value].min() #yapf: disable
			_y_max = self.primary_figure_data_view.loc[_mask][self.primary_bar_top_field_selector.value].max() #yapf: disable
		_primary_y_range_preferred_min = _y_min - (_y_max - _y_min) * 0.03
		_primary_y_range_preferred_max = _y_max + (_y_max - _y_min) * 0.03

		#Fig 2 Y range defaults
		_mask = (self.secondary_figure_data_view['position'] >= _x_range_preferred_min) & (self.secondary_figure_data_view['position'] <= _x_range_preferred_max)#yapf: disable
		if self.secondary_display_type_selector.value == 'Candle':
			_y_min = self.secondary_figure_data_view.loc[_mask][self.secondary_ohlc_l_field_selector.value].min() #yapf: disable
			_y_max = self.secondary_figure_data_view.loc[_mask][self.secondary_ohlc_h_field_selector.value].max() #yapf: disable
		if self.secondary_display_type_selector.value == 'Line':
			_y_min = self.secondary_figure_data_view.loc[_mask][self.secondary_line_field_selector.value].min() #yapf: disable
			_y_max = self.secondary_figure_data_view.loc[_mask][self.secondary_line_field_selector.value].max() #yapf: disable
		if self.secondary_display_type_selector.value == 'Bar':
			_y_min = self.secondary_figure_data_view.loc[_mask][self.secondary_bar_bottom_field_selector.value].min() #yapf: disable
			_y_max = self.secondary_figure_data_view.loc[_mask][self.secondary_bar_top_field_selector.value].max() #yapf: disable
		_secondary_y_range_preferred_min = _y_min - (_y_max - _y_min) * 0.03
		_secondary_y_range_preferred_max = _y_max + (_y_max - _y_min) * 0.03

		#Set Y ranges
		self.primary_figure.y_range.start = _primary_y_range_preferred_min
		self.primary_figure.y_range.end = _primary_y_range_preferred_max
		self.secondary_figure.y_range.start = _secondary_y_range_preferred_min
		self.secondary_figure.y_range.end = _secondary_y_range_preferred_max

	def set_preferred_view_ranges(self, event) -> None:
		#X range preferences
		_x_range_max = self.primary_figure_data_view.index.max() + 5
		_x_range_min = self.primary_figure_data_view.index.min() - 5

		#Set X range
		if self.primary_figure.x_range.start < _x_range_min:
			self.primary_figure.x_range.start = _x_range_min

		if self.primary_figure.x_range.end > _x_range_max:
			self.primary_figure.x_range.end = _x_range_max

		#Y range preferences
		_mask = (self.primary_figure_data_view.index >= self.primary_figure.x_range.start) & \
    (self.primary_figure_data_view.index <= self.primary_figure.x_range.end)
		if self.primary_display_type_selector.value == 'Candle':
			_y_min = self.primary_figure_data_view.loc[_mask][self.primary_ohlc_l_field_selector.value].min() #yapf: disable
			_y_max = self.primary_figure_data_view.loc[_mask][self.primary_ohlc_h_field_selector.value].max() #yapf: disable
		if self.primary_display_type_selector.value == 'Line':
			_y_min = self.primary_figure_data_view.loc[_mask][self.primary_line_field_selector.value].min() #yapf: disable
			_y_max = self.primary_figure_data_view.loc[_mask][self.primary_line_field_selector.value].max() #yapf: disable
		if self.primary_display_type_selector.value == 'Bar':
			_y_min = self.primary_figure_data_view.loc[_mask][self.primary_bar_bottom_field_selector.value].min() #yapf: disable
			_y_max = self.primary_figure_data_view.loc[_mask][self.primary_bar_top_field_selector.value].max() #yapf: disable
		_primary_y_range_preferred_min = _y_min - (_y_max - _y_min) * 0.03
		_primary_y_range_preferred_max = _y_max + (_y_max - _y_min) * 0.03

		_mask = (self.secondary_figure_data_view['position'] >= self.primary_figure.x_range.start) & \
    (self.secondary_figure_data_view['position'] <= self.primary_figure.x_range.end)
		if self.secondary_display_type_selector.value == 'Candle':
			_y_min = self.secondary_figure_data_view.loc[_mask][self.secondary_ohlc_l_field_selector.value].min() #yapf: disable
			_y_max = self.secondary_figure_data_view.loc[_mask][self.secondary_ohlc_h_field_selector.value].max() #yapf: disable
		if self.secondary_display_type_selector.value == 'Line':
			_y_min = self.secondary_figure_data_view.loc[_mask][self.secondary_line_field_selector.value].min() #yapf: disable
			_y_max = self.secondary_figure_data_view.loc[_mask][self.secondary_line_field_selector.value].max() #yapf: disable
		if self.secondary_display_type_selector.value == 'Bar':
			_y_min = self.secondary_figure_data_view.loc[_mask][self.secondary_bar_bottom_field_selector.value].min() #yapf: disable
			_y_max = self.secondary_figure_data_view.loc[_mask][self.secondary_bar_top_field_selector.value].max() #yapf: disable
		_secondary_y_range_preferred_min = _y_min - (_y_max - _y_min) * 0.03
		_secondary_y_range_preferred_max = _y_max + (_y_max - _y_min) * 0.03

		#Set Y range
		self.primary_figure.y_range.start = _primary_y_range_preferred_min
		self.primary_figure.y_range.end = _primary_y_range_preferred_max
		self.secondary_figure.y_range.start = _secondary_y_range_preferred_min
		self.secondary_figure.y_range.end = _secondary_y_range_preferred_max

	def test_func(self, event) -> None:
		_str = f'''
		x_range_start {self.primary_figure.x_range.start}
		x_range_end {self.primary_figure.x_range.end}
		y_range_start {self.primary_figure.y_range.start}
		y_range_end {self.primary_figure.y_range.end}
		'''
		print(_str)