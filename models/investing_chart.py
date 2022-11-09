from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
from bokeh import models
from bokeh import events
import pandas
from datetime import timedelta
from typing import Union


class InvestingChart(BaseModels, DataProvier):
	granularities = {
		'1m': 60,
		'5m': 300,
		'15m': 900,
		'1h': 3600,
		'1d': 86400,
		'1wk': 604800,
		'1mo': 2628000,
		'3mo': 7884000,
	}

	def __init__(self) -> None:
		super().__init__()
		#get figure
		self.figure = self.define_figure(
			x_axis_type='datetime',
			active_scroll='wheel_zoom',
		)
		#define controllers
		self.test_button = self.button(self.test_func, label='test')
		symbols_mapping = self.fetch_symbols_mapping()
		self.instrument_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			self.set_default_x_range,
			self.set_y_range_change,
			options=symbols_mapping['common_name'].values.tolist(),
		)
		self.granularity_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			self.set_default_x_range,
			self.set_y_range_change,
			options=list(self.granularities.keys()),
			sort=False,
		)
		self.portfolio_checkbox_group = self.checkbox_button_group(
			self.set_something,
			labels=['history', 'open'],
		)

		self.set_data_set('', '', '')
		self.set_data_view('', '', '')
		self.set_source('', '', '')
		self.set_default_x_range('', '', ''),
		self.set_y_range_change('', '', ''),

		#Glyphs
		self._segment = self.define_segment(
			x0='index',
			y0='high',
			x1='index',
			y1='low',
			line_color='black',
		)
		self._vbar = self.define_vbar(
			x='index',
			top='open',
			bottom='close',
			fill_color='color',
		)
		self._background_label = self.label(
			text_alpha=0.1,
			text_font_size='32px',
			text_align='left',
			x_units='screen',
			y_units='screen',
		)
		self.set_glyphs('', '', '')
		self.set_default_x_range('', '', '')
		self.set_y_range()

		self.figure.add_glyph(self._source, self._segment)
		self.figure.add_glyph(self._source, self._vbar, name='ohlc')
		self.figure.add_layout(self._background_label)
		#TODO Add tool configurations to base model
		hover = models.HoverTool(
			mode='vline',
			formatters={'@datetime': 'datetime'},
			names=['ohlc'],
			tooltips=[
			('Date', '@datetime{%Y-%m-%d %H:%M:%S}'),
			('Change', '@change{0.0f} %'),
			('Open', '@open{,0.00}'),
			('High', '@high{,0.00}'),
			('Low', '@close{,0.00}'),
			('Close', '@close{,0.00}'),
			],
		)
		#TODO add options to choose tool configuration on runtime (example, for portfolio overlay)
		self.figure.add_tools(
			models.PanTool(),
			models.WheelZoomTool(dimensions='width', speed=1 / 900),
			hover,
			models.CrosshairTool(),
		)
		self.figure.on_event(events.MouseWheel, self.set_y_range_event)
		self.figure.on_event(events.Pan, self.set_y_range_event)

	def set_something(self, attrname, old, new) -> None:
		#TODO cache results
		#TODO destroy glyphs on toggle
		if 0 in self.portfolio_checkbox_group.active:
			print('history')
		else:
			print('no history')
		if 1 in self.portfolio_checkbox_group.active:
			self.open_positions = self.fetch_portfolio_open_positions()
			print('open')
		else:
			print('no open')
		# print(self.portfolio_checkbox_group.labels, self.portfolio_checkbox_group.active,)

	def set_glyphs(self, attrname, old, new) -> None:
		_w = 0.5
		self._vbar.update(width=(_w))
		self._background_label.update(
			text=f'{self.instrument_selector.value} - {self.granularity_selector.value}'
		)
		self.figure.xaxis.major_label_overrides = self.data_view['datetime'].dt.strftime(
			'%Y-%m-%d %H:%M:%S'
		).to_dict()

	def set_data_set(self, attrname, old, new) -> None:
		self.data_set = self.fetch_investing_instrument(
			symbol=self.instrument_selector.value,
			granularity=self.granularity_selector.value,
		)
		print('data set set')

	def set_data_view(self, attrname, old, new) -> None:
		#TODO fix datetime dtypes in portfolio prj
		#TODO glyphs should get created and destroyed with change of widget
		#TODO add separate event handler for portfolio glyphs
		#TODO make portfolio glyphs scale with selected granularity
		#TODO make portfolio glyphs easier to read
		self.data_view = self.data_set
		#Order values by datetime
		self.data_view.sort_values(by='datetime', ascending=True, inplace=True)
		#Define change
		self.data_view['change'] = (self.data_view['close']
			- self.data_view['close'].shift(1)) / self.data_view['close'].shift(1) * 100
		#Define vbar color
		self.data_view['color'] = 'red'
		self.data_view.loc[self.data_view['change'] > 0, 'color'] = 'green'
		#Override index
		self.data_view.reset_index(inplace=True, drop=True)
		# print(self.data_view.head(10))
		# print(self.data_view['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').to_dict())
		# try:
		# 	self.portfolio_view = self.open_positions
		# 	self.portfolio_view = self.portfolio_view.loc[self.portfolio_view['common_name'] ==
		# 		self.instrument_selector.value]
		# 	self.portfolio_view['open_datetime'] = pandas.to_datetime(self.portfolio_view['open_datetime'])
		# 	self.saus = self.column_data_source(self.portfolio_view)
		# 	self.positions_glyph = self.define_circle(fill_color='orange', x='open_datetime', y='open_rate')
		# 	self.sl_glyph = self.define_circle(fill_color='red', x='open_datetime', y='stop_loss_rate')
		# 	self.figure.add_glyph(self.saus, self.positions_glyph)
		# 	self.figure.add_glyph(self.saus, self.sl_glyph)
		# 	_w = self.granularities[self.granularity_selector.value] / 10000
		# 	self.positions_glyph.update(size=(_w), x='open_datetime', y='open_rate')
		# 	self.sl_glyph.update(size=(_w), x='open_datetime', y='stop_loss_rate')
		# except Exception as e:
		# 	print(repr(e))

	def set_source(self, attrname, old, new) -> None:
		try:
			self._source.data.update(self.column_data_source(self.data_view).data)
			# self._source.data = self.data_view.to_dict(orient='list')
			print('source updated')
		except AttributeError:
			self._source = self.column_data_source(self.data_view)
			print('source created')

	def set_default_x_range(self, attrname, old, new) -> None:
		self.figure.x_range.update(end=self.data_view.index.max() + 5)
		self.figure.x_range.update(start=self.data_view.index.max() - 180)

	def set_y_range_change(self, attrname, old, new) -> None:
		"""Horribly uggly but due to bokeh limitations
		can't call same function with on change or on events.
		Further, python doesn't support overloading of functions so...
		"""
		self.set_y_range()

	def set_y_range_event(self, event) -> None:
		self.set_y_range()

	def set_y_range(self) -> None:
		_mask = (self.data_view.index >=
			self.figure.x_range.start) & (self.data_view.index <= self.figure.x_range.end)
		_min = self.data_view.loc[_mask]['low'].min()
		_max = self.data_view.loc[_mask]['high'].max()
		self.figure.y_range.start = _min
		self.figure.y_range.end = _max

	def test_func(self, event) -> None:
		_str = f'''
		x_range_start {self.figure.x_range.start}
		x_range_end {self.figure.x_range.end}
		y_range_start {self.figure.y_range.start}
		y_range_end {self.figure.y_range.end}
		'''
		print(_str)