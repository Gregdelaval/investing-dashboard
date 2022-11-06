from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
from bokeh import models
from bokeh import events
from datetime import datetime
import pandas


class InvestingChart(BaseModels, DataProvier):

	def __init__(self) -> None:
		super().__init__()
		#set data
		granularity = '1m'
		symbol = 'NDX'
		_data = self.fetch_investing_instrument(symbol=symbol, granularity=granularity)
		_data['color'] = 'red'
		_data.loc[_data['close'] > _data['open'], 'color'] = 'green'
		self._data = _data
		#set source
		_source = self.column_data_source(_data)

		#get glyphs
		_segment = self.define_segment(
			x0='datetime',
			y0='high',
			x1='datetime',
			y1='low',
		)
		_vbar = self.define_vbar(
			x='datetime',
			width=60 * 1000,
			top='open',
			bottom='close',
			fill_color='color',
		)
		_background_label = models.Label(
			x=70,
			y=70,
			x_units='screen',
			y_units='screen',
			text_color='white',
		)

		#get figure
		_figure = self.define_figure(
			x_axis_type="datetime",
			sizing_mode='scale_height',
		)
		_figure.add_tools(
			models.PanTool(dimensions='width'),
			models.WheelZoomTool(dimensions='width'),
		)
		_figure.add_glyph(_source, _segment)
		_figure.add_glyph(_source, _vbar)
		_figure.add_layout(_background_label)
		_figure.on_event(events.MouseWheel, self.scroll_event)
		_figure.on_event(events.Pan, self.scroll_event)
		_background_label.update(text=f'{symbol} - {granularity}')
		self.test_figure = _figure

	def scroll_event(self, event) -> None:
		_start = pandas.to_datetime(self.test_figure.x_range.start, unit="ms")
		_end = pandas.to_datetime(self.test_figure.x_range.end, unit="ms")
		_mask = (self._data['datetime'] >= _start) & (self._data['datetime'] <= _end)
		_min = self._data.loc[_mask]['low'].min()
		_max = self._data.loc[_mask]['high'].max()
		self.test_figure.y_range.start = _min
		self.test_figure.y_range.end = _max
