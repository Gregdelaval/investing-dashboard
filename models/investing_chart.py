from .base_models import BaseModels
from ..helpers.helpers import Helpers
from ..helpers.data_provider import DataProvier
from bokeh import models, events
from functools import partial
import pandas
import numpy


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
		symbols_mapping = self.fetch_symbols_mapping()['common_name'].values.tolist()

		#define labels
		self.primary_axis_header = self.divider(text='Primary figure')
		self.primary_axis_portfolio_descriptor = self.pretext(text='Show investments')
		self.secondary_axis_header = self.divider(text='Secondary figure')

		#Data set controllers
		self.trigger_calculation_button = self.button(
			self.set_data_set,
			self.orchestrate_data_view_setting,
			self.set_source,
			self.set_glyphs,
			self.set_tools,
			partial(self.set_view_ranges, x_min=180, x_max=5),
			label='Update',
		)
		self.primary_instrument_selector = self.selector(
			title='Instrument',
			options=symbols_mapping,
		)
		self.primary_granularity_selector = self.selector(
			options=list(self.granularities.keys()),
			title='Granularity',
			sort=False,
		)
		self.secondary_instrument_selector = self.selector(
			title='Instrument',
			options=symbols_mapping,
		)
		self.secondary_granularity_selector = self.selector(
			options=list(self.granularities.keys()),
			title='Granularity',
			sort=False,
		)
		self.set_data_set()
		#Primary glyph controllers
		self.primary_display_type_selector = self.selector(
			partial(self.set_controllers, caller='primary_display_type_selector'),
			title='Display Type',
			options=self.data_display_types,
			sort=False,
		)
		self.primary_line_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Line based on field',
			visible=False,
		)
		self.primary_ohlc_o_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Open',
			value='open',
			visible=False,
		)
		self.primary_ohlc_h_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='High',
			value='high',
			visible=False,
		)
		self.primary_ohlc_l_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Low',
			value='low',
			visible=False,
		)
		self.primary_ohlc_c_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Close',
			value='close',
			visible=False,
		)
		self.primary_bar_top_field_selector = self.selector(
			options=self.primary_figure_data_set.columns.tolist(),
			title='Top',
			value='volume',
			visible=False,
		)
		self.portfolio_open_positions_toggle = self.define_toggle(
			self.set_data_set,
			self.orchestrate_data_view_setting,
			self.set_source,
			self.set_glyphs,
			label='Open Positions',
		)
		self.portfolio_historical_positions_toggle = self.define_toggle(
			self.set_data_set,
			self.orchestrate_data_view_setting,
			self.set_source,
			self.set_glyphs,
			label='Historical Positions',
		)
		#Secondary glyph controllers
		secondary_columns = self.secondary_figure_data_set.columns.tolist()
		secondary_columns.append('0')
		self.secondary_display_type_selector = self.selector(
			partial(self.set_controllers, caller='secondary_display_type_selector'),
			title='Display Type',
			options=self.data_display_types,
			sort=False,
			name='secondary_display_type_selector',
		)
		self.secondary_line_field_selector = self.selector(
			options=secondary_columns,
			title='Line based on field',
			visible=False,
		)
		self.secondary_ohlc_o_field_selector = self.selector(
			options=secondary_columns,
			title='Open',
			value='open',
			visible=False,
		)
		self.secondary_ohlc_h_field_selector = self.selector(
			options=secondary_columns,
			title='High',
			value='high',
			visible=False,
		)
		self.secondary_ohlc_l_field_selector = self.selector(
			options=secondary_columns,
			title='Low',
			value='low',
			visible=False,
		)
		self.secondary_ohlc_c_field_selector = self.selector(
			options=secondary_columns,
			title='Close',
			value='close',
			visible=False,
		)
		self.secondary_bar_top_field_selector = self.selector(
			options=secondary_columns,
			title='Top',
			value='volume',
			visible=False,
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
			x='position',
			top='volume',
			bottom=0,
			fill_color='color',
			width=0.5,
		)
		self._primary_figure_line = self.define_line(
			x='position',
			y='close',
		)
		self._primary_axis_ohlc_candle_line = self.define_segment(
			x0='position',
			y0='high',
			x1='position',
			y1='low',
			line_color='black',
		)
		self._primary_axis_ohlc_candle_bar = self.define_vbar(
			x='position',
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

		#Tools
		tools = (
			models.CrosshairTool(overlay=(models.Span(dimension="width"), models.Span(dimension="height"))),
			models.WheelZoomTool(dimensions='width', speed=0.2),
		)

		#Invoke model event handlers
		self.orchestrate_data_view_setting()
		self.set_source()
		self.set_controllers()

		#Primary figure
		self.primary_figure = self.define_figure(
			output_backend="webgl",
			x_axis_type='datetime',
			active_scroll='wheel_zoom',
			width=self.chart_width,
			height=int((7 * self.chart_height) / 9),
			y_range=(
			self.primary_figure_data_view['close'].min(),
			self.primary_figure_data_view['close'].max(),
			),
			x_range=(0, self.primary_figure_data_view['position'].max()),
		)
		self.primary_figure.add_glyph(self._primary_source, self._primary_figure_line)
		self.primary_figure.add_glyph(self._primary_source, self._primary_vbar)
		self.primary_figure.add_glyph(self._primary_source, self._primary_axis_ohlc_candle_line)
		self.primary_candle_glyph = self.primary_figure.add_glyph(self._primary_source, self._primary_axis_ohlc_candle_bar) # yapf: disable
		self.primary_figure.add_glyph(self._historical_positions_source, self._historical_position_connector_glyph)  # yapf: disable
		self.primary_figure.add_glyph(self._historical_positions_source, self._historical_open_positions_glyph)# yapf: disable
		self.primary_figure.add_glyph(self._historical_positions_source, self._historical_close_positions_glyph) # yapf: disable
		self.primary_figure.add_glyph(self._open_positions_source, self._open_positions_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._stop_loss_vline_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._stop_loss_hline_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._take_profit_hline_glyph)
		self.primary_figure.add_glyph(self._open_positions_source, self._take_profit_vline_glyph)
		self.primary_figure.add_layout(self._background_label, 'center')
		self.primary_figure.add_tools(*tools, self.define_hover_tool())
		self.primary_figure.on_event(events.MouseWheel, self.set_view_ranges)

		#Secondary figure
		self.secondary_figure = self.define_figure(
			output_backend="webgl",
			x_axis_type=None,
			active_scroll='wheel_zoom',
			width=self.chart_width,
			height=int((2 * self.chart_height) / 9),
			y_range=(
			self.secondary_figure_data_view['close'].min(),
			self.secondary_figure_data_view['close'].max(),
			),
			x_range=self.primary_figure.x_range,
		)
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_figure_line)
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_vbar)
		self.secondary_candle_glyph = self.secondary_figure.add_glyph(
			self._secondary_source, self._secondary_axis_ohlc_candle_line
		)
		self.secondary_figure.add_glyph(self._secondary_source, self._secondary_axis_ohlc_candle_bar)
		self.secondary_figure.add_tools(*tools, self.define_hover_tool())
		self.secondary_figure.on_event(events.MouseWheel, self.set_view_ranges)

		#Invoke view event handlers
		self.set_glyphs()
		self.set_view_ranges(x_min=180, x_max=5)
		self.set_tools()

	def set_tools(self):
		#Set renderers
		self.primary_figure.select_one('hover_tool').renderers = [self.primary_candle_glyph]
		self.secondary_figure.select_one('hover_tool').renderers = [self.secondary_candle_glyph]

		#Set tooltip formats
		_datetime_format = self.granularities[self.primary_granularity_selector.value]['format']
		self.primary_figure.select_one('hover_tool').formatters = {
			'@datetime': 'datetime'
		}
		self.primary_figure.select_one('hover_tool').tooltips = [
			('Date', '@datetime{%s}' % _datetime_format)
		]
		self.secondary_figure.select_one('hover_tool').formatters = {
			'@datetime': 'datetime'
		}
		self.secondary_figure.select_one('hover_tool').tooltips = [
			('Date', '@datetime{%s}' % _datetime_format)
		]

		if self.primary_display_type_selector.value == 'Line':
			_value = self.primary_line_field_selector.value
			self.primary_figure.select_one('hover_tool').tooltips.extend([(_value, '@%s{0.0[00]a}' % _value)]
																																																															)
		if self.primary_display_type_selector.value == 'Candle':
			self.primary_figure.select_one('hover_tool').tooltips.extend([
				('open', '@%s{0.0[00]a}' % self.primary_ohlc_o_field_selector.value),
				('high', '@%s{0.0[00]a}' % self.primary_ohlc_h_field_selector.value),
				('low', '@%s{0.0[00]a}' % self.primary_ohlc_l_field_selector.value),
				('close', '@%s{0.0[00]a}' % self.primary_ohlc_c_field_selector.value),
			])
		if self.primary_display_type_selector.value == 'Bar':
			_value = self.primary_bar_top_field_selector.value
			self.primary_figure.select_one('hover_tool').tooltips.extend([(_value, '@%s{0.[00]a}' % _value)])

		if self.secondary_display_type_selector.value == 'Line':
			_value = self.secondary_line_field_selector.value
			self.secondary_figure.select_one('hover_tool').tooltips.extend([
				(_value, '@%s{0.0[00]a}' % _value)
			])
		if self.secondary_display_type_selector.value == 'Candle':
			self.secondary_figure.select_one('hover_tool').tooltips.extend([
				('open', '@%s{0.0[00]a}' % self.secondary_ohlc_o_field_selector.value),
				('high', '@%s{0.0[00]a}' % self.secondary_ohlc_h_field_selector.value),
				('low', '@%s{0.0[00]a}' % self.secondary_ohlc_l_field_selector.value),
				('close', '@%s{0.0[00]a}' % self.secondary_ohlc_c_field_selector.value),
			])
		if self.secondary_display_type_selector.value == 'Bar':
			_value = self.secondary_bar_top_field_selector.value
			self.secondary_figure.select_one('hover_tool').tooltips.extend([
				(_value, '@%s{0.[00]a}' % _value)
			])

	def set_controllers(
		self,
		caller: str = None,
	) -> None:
		self.primary_line_field_selector.options = self.primary_figure_data_view.columns.tolist()
		self.secondary_line_field_selector.options = self.secondary_figure_data_view.columns.tolist()
		if caller == 'primary_display_type_selector':
			self.primary_line_field_selector.visible = False
			self.primary_ohlc_o_field_selector.visible = False
			self.primary_ohlc_h_field_selector.visible = False
			self.primary_ohlc_l_field_selector.visible = False
			self.primary_ohlc_c_field_selector.visible = False
			self.primary_bar_top_field_selector.visible = False
		if caller == 'secondary_display_type_selector':
			self.secondary_line_field_selector.visible = False
			self.secondary_ohlc_o_field_selector.visible = False
			self.secondary_ohlc_h_field_selector.visible = False
			self.secondary_ohlc_l_field_selector.visible = False
			self.secondary_ohlc_c_field_selector.visible = False
			self.secondary_bar_top_field_selector.visible = False
		if self.primary_display_type_selector.value == 'Line':
			self.primary_line_field_selector.visible = True
		if self.primary_display_type_selector.value == 'Candle':
			self.primary_ohlc_o_field_selector.visible = True
			self.primary_ohlc_h_field_selector.visible = True
			self.primary_ohlc_l_field_selector.visible = True
			self.primary_ohlc_c_field_selector.visible = True
		if self.primary_display_type_selector.value == 'Bar':
			self.primary_bar_top_field_selector.visible = True
		if self.secondary_display_type_selector.value == 'Line':
			self.secondary_line_field_selector.visible = True
		if self.secondary_display_type_selector.value == 'Candle':
			self.secondary_ohlc_o_field_selector.visible = True
			self.secondary_ohlc_h_field_selector.visible = True
			self.secondary_ohlc_l_field_selector.visible = True
			self.secondary_ohlc_c_field_selector.visible = True
		if self.secondary_display_type_selector.value == 'Bar':
			self.secondary_bar_top_field_selector.visible = True

	def set_glyphs(self) -> None:
		#Update background label
		self._background_label.update(
			text=f'{self.primary_instrument_selector.value} - {self.primary_granularity_selector.value}'
		)
		#Update x axis format label
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
			self._historical_position_connector_glyph.line_width = 0.5
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
			granularity=self.secondary_granularity_selector.value,
		)
		self.open_positions_data_set = self.fetch_portfolio_open_positions()
		self.historical_positions_data_set = self.fetch_portfolio_historical_positions()

	def orchestrate_data_view_setting(self) -> None:
		# Define data views
		self.primary_figure_data_view = self.primary_figure_data_set
		self.secondary_figure_data_view = self.secondary_figure_data_set
		self.open_positions_view = self.open_positions_data_set
		self.historical_positions_view = self.historical_positions_data_set

		#Calculate chart views
		self.set_chart_views()

		#Calculate portfolio positions
		if self.portfolio_open_positions_toggle.active:
			self.set_open_positions_data_view()
		if self.portfolio_historical_positions_toggle.active:
			self.set_historical_positions_data_view()

	def set_chart_views(self):
		#Calculate figures
		for view in [self.primary_figure_data_view, self.secondary_figure_data_view]:
			view.sort_values(by='datetime', ascending=True, inplace=True)
			view['change'] = (view['close'] - view['close'].shift(1)) / view['close'].shift(1) * 100
			view['fluctuation'] = (view['high'] - view['low']) / view['high'] * 100
			view['color'] = numpy.select([view['change'] > 0, view['change'] < 0], ['green', 'red'])
			view.reset_index(inplace=True, drop=True)
		self.primary_figure_data_view['position'] = self.primary_figure_data_view.index

		#Map index positions
		self.secondary_figure_data_view = Helpers().match_closest_neighbor_index(
			parent_df=self.primary_figure_data_view,
			child_df=self.secondary_figure_data_view,
			parent_merge_on='datetime',
			child_merge_on='datetime',
		)

	def set_open_positions_data_view(self):
		#TODO fix datetime dtypes in portfolio prj
		self.open_positions_view['open_datetime'] = pandas.to_datetime(
			self.open_positions_view['open_datetime']
		)

		#Map index positions
		self.open_positions_view.sort_values(by='open_datetime', ascending=True, inplace=True)
		self.open_positions_view = Helpers().match_closest_neighbor_index(
			parent_df=self.primary_figure_data_view,
			child_df=self.open_positions_view,
			parent_merge_on='datetime',
			child_merge_on='open_datetime',
		)

		#Calculate view content
		self.open_positions_view = self.open_positions_view.loc[self.open_positions_view['common_name'] ==
			self.primary_instrument_selector.value]
		self.open_positions_view = self.open_positions_view.loc[self.open_positions_view['position'] != 0]
		self.open_positions_view['marker'] = 'triangle'
		self.open_positions_view.loc[self.open_positions_view['is_buy'] == 0,
			'marker'] = 'inverted_triangle'
		self.open_positions_view['position_neg_offset'] = self.open_positions_view['position'] - 1
		self.open_positions_view['position_pos_offset'] = self.open_positions_view['position'] + 1

	def set_historical_positions_data_view(self):
		#TODO fix datetime dtypes in portfolio prj
		self.historical_positions_view['open_datetime'] = pandas.to_datetime(
			self.historical_positions_view['open_datetime']
		)
		self.historical_positions_view['close_datetime'] = pandas.to_datetime(
			self.historical_positions_view['close_datetime']
		)

		#Map index positions
		self.historical_positions_view = self.historical_positions_view.sort_values(
			by='open_datetime', ascending=True
		)
		self.historical_positions_view = Helpers().match_closest_neighbor_index(
			parent_df=self.primary_figure_data_view,
			child_df=self.historical_positions_view,
			parent_merge_on='datetime',
			child_merge_on='open_datetime',
			appended_neighbor_index_col_name='open_position',
		)
		self.historical_positions_view = self.historical_positions_view.sort_values(
			by='close_datetime', ascending=True
		)
		self.historical_positions_view = Helpers().match_closest_neighbor_index(
			parent_df=self.primary_figure_data_view,
			child_df=self.historical_positions_view,
			parent_merge_on='datetime',
			child_merge_on='close_datetime',
			appended_neighbor_index_col_name='close_position',
		)

		#Calculate view content
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

	def set_view_ranges(self, event=None, x_min: int = None, x_max: int = None) -> None:
		#X ranges
		if x_min:
			_x_range_min = self.primary_figure_data_view['position'].max() - x_min
			self.primary_figure.x_range.start = self.secondary_figure.x_range.start = _x_range_min
		else:
			_x_range_min = self.primary_figure.x_range.start

		if x_max:
			_x_range_max = self.primary_figure_data_view['position'].max() + x_max
			self.primary_figure.x_range.end = self.secondary_figure.x_range.end = _x_range_max
		else:
			_x_range_max = self.primary_figure.x_range.end

		#y ranges
		self.primary_figure.y_range.start, self.primary_figure.y_range.end = calculate_y_range(
			display_type_selector=self.primary_display_type_selector,
			ohlc_l_selector=self.primary_ohlc_l_field_selector,
			ohlc_h_selector=self.primary_ohlc_h_field_selector,
			line_field_selector=self.primary_line_field_selector,
			bar_top_field_selector=self.primary_bar_top_field_selector,
			data_view=self.primary_figure_data_view,
			x_min=_x_range_min,
			x_max=_x_range_max,
		)
		self.secondary_figure.y_range.start, self.secondary_figure.y_range.end = calculate_y_range(
			self.secondary_display_type_selector,
			self.secondary_ohlc_l_field_selector,
			self.secondary_ohlc_h_field_selector,
			self.secondary_line_field_selector,
			self.secondary_bar_top_field_selector,
			self.secondary_figure_data_view,
			_x_range_min,
			_x_range_max,
		)


def calculate_y_range(
	display_type_selector: models.Select,
	ohlc_l_selector: models.Select,
	ohlc_h_selector: models.Select,
	line_field_selector: models.Select,
	bar_top_field_selector: models.Select,
	data_view: pandas.DataFrame,
	x_min: int,
	x_max: int,
) -> None:
	_mask = (data_view['position'] >= x_min) & (data_view['position'] <= x_max)
	if display_type_selector.value == 'Candle':
		_y_min = data_view.loc[_mask][ohlc_l_selector.value].min()
		_y_max = data_view.loc[_mask][ohlc_h_selector.value].max()
	if display_type_selector.value == 'Line':
		print(data_view)
		_y_min = data_view.loc[_mask][line_field_selector.value].min()
		_y_max = data_view.loc[_mask][line_field_selector.value].max()
	if display_type_selector.value == 'Bar':
		_y_min = 0
		_y_max = data_view.loc[_mask][bar_top_field_selector.value].max()
	_y_min = _y_min - (_y_max - _y_min) * 0.03
	_y_max = _y_max + (_y_max - _y_min) * 0.03
	return (_y_min, _y_max)
