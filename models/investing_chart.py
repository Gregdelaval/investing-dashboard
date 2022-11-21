from .base_models import BaseModels
from ..helpers.helpers import Helpers
from ..helpers.data_provider import DataProvier
from bokeh import models, events
import pandas
from datetime import datetime


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

	def __init__(
		self,
		chart_width: int,
		chart_height: int,
	) -> None:
		super().__init__()
		#Set chart dimensions
		self.chart_width = chart_width
		self.chart_height = chart_height

		#define controllers
		self.test_button = self.button(self.test_func, label='test')
		symbols_mapping = self.fetch_symbols_mapping()
		self.instrument_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			self.set_default_view_ranges,
			options=symbols_mapping['common_name'].values.tolist(),
		)
		self.granularity_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			self.set_default_view_ranges,
			options=list(self.granularities.keys()),
			sort=False,
		)
		self.portfolio_open_positions_toggle = self.define_toggle(
			self.set_glyphs,
			self.set_default_view_ranges,
			active=False,
			label='Open Positions',
		)
		self.portfolio_historical_positions_toggle = self.define_toggle(
			self.set_glyphs,
			self.set_default_view_ranges,
			active=False,
			label='Historical Positions',
		)

		#Glyphs
		self._info_box = self.define_box_annotation(
			left_units='screen',
			right_units='screen',
			top_units='screen',
			bottom_units='screen',
			left=self.chart_width * 0.82,
			right=self.chart_width * 1.1,
			bottom=self.chart_height * 0.80,
			top=self.chart_height * 1.1,
			fill_alpha=0.5,
			fill_color='#242424',
		)
		self._background_label = self.label(
			text_alpha=0.1,
			text_font_size='32px',
			text_align='center',
			x_units='screen',
			y_units='screen',
			x=self.chart_width * 0.5,
			y=self.chart_height * 0.75,
		)
		self._ohlc_candle_line = self.define_segment(
			x0='index',
			y0='high',
			x1='index',
			y1='low',
			line_color='black',
		)
		self._ohlc_candle_bar = self.define_vbar(
			x='index',
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
			x='open_position',
			y='open_rate',
			marker='marker',
			fill_color='gray',
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
			names=['ohlc'],
		)

		#Invoke model event handlers
		self.set_data_set('', '', '')
		self.set_data_view('', '', '')
		self.set_source('', '', '')

		#Define figure
		#TODO overlay showing leverage distances
		self.figure = self.define_figure(
			x_axis_type='datetime',
			active_scroll='wheel_zoom',
			width=self.chart_width,
			height=self.chart_height,
			y_range=(self.ohlc_data_view['close'].min(), self.ohlc_data_view['close'].max()),
			x_range=(0, self.ohlc_data_view.index.max()),
		)
		self.figure.yaxis.ticker.desired_num_ticks = 25
		self.figure.xaxis.ticker.desired_num_ticks = 10
		self.figure.add_glyph(self._ohlc_source, self._ohlc_candle_line)
		self.figure.add_glyph(self._ohlc_source, self._ohlc_candle_bar, name='ohlc')
		self.figure.add_glyph(
			self._historical_positions_source, self._historical_position_connector_glyph
		)
		self.figure.add_glyph(self._historical_positions_source, self._historical_open_positions_glyph)
		self.figure.add_glyph(self._historical_positions_source, self._historical_close_positions_glyph)
		self.figure.add_glyph(self._open_positions_source, self._open_positions_glyph)
		self.figure.add_glyph(self._open_positions_source, self._stop_loss_vline_glyph)
		self.figure.add_glyph(self._open_positions_source, self._stop_loss_hline_glyph)
		self.figure.add_glyph(self._open_positions_source, self._take_profit_hline_glyph)
		self.figure.add_glyph(self._open_positions_source, self._take_profit_vline_glyph)
		self.figure.add_layout(self._background_label, 'center')
		self.figure.add_layout(self._info_box, 'center')
		self.figure.add_tools(
			models.PanTool(),
			models.WheelZoomTool(dimensions='width', speed=1 / 900),
			hover,
			models.CrosshairTool(),
		)
		self.figure.on_event(events.MouseWheel, self.set_preferred_view_ranges)

		#Invoke view event handlers
		self.set_glyphs('', '', '')
		self.set_default_view_ranges('', '', '')

	def set_glyphs(self, attrname, old, new) -> None:
		self._background_label.update(
			text=f'{self.instrument_selector.value} - {self.granularity_selector.value}'
		)
		self.figure.xaxis.major_label_overrides = self.ohlc_data_view['datetime'].dt.strftime(
			self.granularities[self.granularity_selector.value]['format']
		).to_dict()
		self.figure.yaxis.formatter = models.NumeralTickFormatter(format='0')

		if self.portfolio_historical_positions_toggle.active:
			self._historical_open_positions_glyph.size = 10
			self._historical_close_positions_glyph.size = 8
			self._historical_position_connector_glyph.line_width = 0.3
		else:
			self._historical_open_positions_glyph.size = 0
			self._historical_close_positions_glyph.size = 0
			self._historical_position_connector_glyph.line_width = 0
		if self.portfolio_open_positions_toggle.active:
			self._open_positions_glyph.size = 10
			self._stop_loss_vline_glyph.line_width = 0.3
			self._stop_loss_hline_glyph.line_width = 0.7
			self._take_profit_hline_glyph.line_width = 0.7
			self._take_profit_vline_glyph.line_width = 0.3
		else:
			self._take_profit_vline_glyph.line_width = 0
			self._take_profit_hline_glyph.line_width = 0
			self._stop_loss_vline_glyph.line_width = 0
			self._stop_loss_hline_glyph.line_width = 0
			self._open_positions_glyph.size = 0

	def set_data_set(self, attrname, old, new) -> None:
		self.ohlc_data_set = self.fetch_investing_instrument(
			symbol=self.instrument_selector.value,
			granularity=self.granularity_selector.value,
		)
		self.open_positions_data_set = self.fetch_portfolio_open_positions()
		self.historical_positions_data_set = self.fetch_portfolio_historical_positions()

	def set_data_view(self, attrname, old, new) -> None:
		#TODO fix datetime dtypes in portfolio prj
		###OHLC DATA VIEW###
		self.ohlc_data_view = self.ohlc_data_set
		#Order values by datetime
		self.ohlc_data_view.sort_values(by='datetime', ascending=True, inplace=True)
		#Define change
		self.ohlc_data_view['change'] = (
			self.ohlc_data_view['close'] - self.ohlc_data_view['close'].shift(1)
		) / self.ohlc_data_view['close'].shift(1) * 100
		#Define vbar color
		self.ohlc_data_view['color'] = 'red'
		self.ohlc_data_view.loc[self.ohlc_data_view['open'] < self.ohlc_data_view['close'],
			'color'] = 'green'
		# reset index
		self.ohlc_data_view.reset_index(inplace=True, drop=True)

		###OPEN POSITIONS DATA VIEW###
		self.open_positions_view = self.open_positions_data_set
		self.open_positions_view['open_datetime'] = pandas.to_datetime(
			self.open_positions_view['open_datetime']
		)
		#Set index position
		self.open_positions_view['position'] = self.open_positions_view['open_datetime'].apply(
			lambda x: Helpers().find_closest_neighbour(
			for_value=x,
			in_df=self.ohlc_data_view,
			in_column='datetime',
			)
		)
		self.open_positions_view = self.open_positions_view.loc[self.open_positions_view['common_name'] ==
			self.instrument_selector.value]
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
			in_df=self.ohlc_data_view,
			in_column='datetime',
			)
		)
		self.historical_positions_view['close_position'] = self.historical_positions_view['close_datetime'].apply( # yapf: disable
			lambda x: Helpers().find_closest_neighbour(
			for_value=x,
			in_df=self.ohlc_data_view,
			in_column='datetime',
			)
		)
		self.historical_positions_view = self.historical_positions_view.loc[
			self.historical_positions_view['common_name'] == self.instrument_selector.value]
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
		self.historical_positions_view.loc[_shorting_mask, 'closing_color'] = 'green'

	def set_source(self, attrname, old, new) -> None:
		try:
			self._ohlc_source.data.update(self.column_data_source(self.ohlc_data_view).data)
			self._open_positions_source.data = self.open_positions_view.to_dict(orient='list')
			self._historical_positions_source.data = self.historical_positions_view.to_dict(orient='list')
		except AttributeError:
			self._ohlc_source = self.column_data_source(self.ohlc_data_view)
			self._open_positions_source = self.column_data_source(self.open_positions_view)
			self._historical_positions_source = self.column_data_source(self.historical_positions_view)

	def set_default_view_ranges(self, attrname, old, new) -> None:
		#X range defaults
		_x_range_preferred_min = self.ohlc_data_view.index.max() - 180
		_x_range_preferred_max = self.ohlc_data_view.index.max() + 5

		#Set X ranges
		self.figure.x_range.start = _x_range_preferred_min
		self.figure.x_range.end = _x_range_preferred_max

		#Y range defaults
		_mask = (self.ohlc_data_view.index >=
			_x_range_preferred_min) & (self.ohlc_data_view.index <= _x_range_preferred_max)
		_y_min = self.ohlc_data_view.loc[_mask]['low'].min()
		_y_max = self.ohlc_data_view.loc[_mask]['high'].max()
		_y_range_preferred_min = _y_min - (_y_max - _y_min) * 0.03
		_y_range_preferred_max = _y_max + (_y_max - _y_min) * 0.03

		#Set Y ranges
		self.figure.y_range.start = _y_range_preferred_min
		self.figure.y_range.end = _y_range_preferred_max

	def set_preferred_view_ranges(self, event) -> None:
		#X range preferences
		_x_range_max = self.ohlc_data_view.index.max() + 5
		_x_range_min = self.ohlc_data_view.index.min() - 5

		#Set X range
		if self.figure.x_range.start < _x_range_min:
			self.figure.x_range.start = _x_range_min

		if self.figure.x_range.end > _x_range_max:
			self.figure.x_range.end = _x_range_max

		#Y range preferences
		_mask = (self.ohlc_data_view.index >=
			self.figure.x_range.start) & (self.ohlc_data_view.index <= self.figure.x_range.end)
		_y_min = self.ohlc_data_view.loc[_mask]['low'].min()
		_y_max = self.ohlc_data_view.loc[_mask]['high'].max()
		_y_range_preferred_min = _y_min - (_y_max - _y_min) * 0.03
		_y_range_preferred_max = _y_max + (_y_max - _y_min) * 0.03

		#Set Y range
		self.figure.y_range.start = _y_range_preferred_min
		self.figure.y_range.end = _y_range_preferred_max

	def test_func(self, event) -> None:
		_str = f'''
		x_range_start {self.figure.x_range.start}
		x_range_end {self.figure.x_range.end}
		y_range_start {self.figure.y_range.start}
		y_range_end {self.figure.y_range.end}
		'''
		print(_str)