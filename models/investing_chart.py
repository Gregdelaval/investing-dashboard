from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
from bokeh import models
from bokeh import events
import pandas


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
		#define controllers
		symbols_mapping = self.fetch_symbols_mapping()
		self.instrument_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			options=symbols_mapping['common_name'].values.tolist(),
		)
		self.granularity_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_glyphs,
			options=list(self.granularities.keys()),
			sort=False,
		)

		self.set_data_set('', '', '')
		self.set_data_view('', '', '')
		self.set_source('', '', '')
		#Glyphs
		self._segment = self.define_segment(
			x0='datetime',
			y0='high',
			x1='datetime',
			y1='low',
			line_color='black',
		)
		self._vbar = self.define_vbar(
			x='datetime',
			top='open',
			bottom='close',
			fill_color='color',
		)
		self._background_label = models.Label(
			x=70,
			y=70,
			x_units='screen',
			y_units='screen',
			text_color='white',
		)
		self.set_glyphs('', '', '')
		#get figure
		self.figure = self.define_figure(x_axis_type='datetime',)
		self.figure.add_glyph(self._source, self._segment)
		self.figure.add_glyph(self._source, self._vbar, name='ohlc')
		self.figure.add_layout(self._background_label)
		hover = models.HoverTool( #Add to base models
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
		self.figure.add_tools(
			models.PanTool(dimensions='width'),
			models.WheelZoomTool(dimensions='width'),
			hover,
			models.CrosshairTool(dimensions='height'),
		)
		self.figure.on_event(events.MouseWheel, self.set_view_range)
		self.figure.on_event(events.Pan, self.set_view_range)
		self.figure.xgrid.grid_line_color = None  #add as defaults to figures
		self.figure.ygrid.grid_line_color = None
		self.figure.background_fill_alpha = 0.5

	def set_glyphs(self, attrname, old, new) -> None:
		_w = 800 * self.granularities[self.granularity_selector.value]
		self._vbar.update(width=(_w))
		self._background_label.update(
			text=f'{self.instrument_selector.value} - {self.granularity_selector.value}'
		)

	def set_data_set(self, attrname, old, new) -> None:
		self.data_set = self.fetch_investing_instrument(
			symbol=self.instrument_selector.value,
			granularity=self.granularity_selector.value,
		)

	def set_data_view(self, attrname, old, new) -> None:
		self.data_view = self.data_set
		#Order values by datetime
		self.data_view.sort_values(by='datetime', ascending=False, inplace=True)
		#Define change
		self.data_view['change'] = (self.data_view['close']
			- self.data_view['close'].shift(-1)) / self.data_view['close'].shift(-1) * 100
		#Define vbar color
		self.data_view['color'] = 'red'
		self.data_view.loc[self.data_view['change'] > 0, 'color'] = 'green'

	def set_source(self, attrname, old, new) -> None:
		try:
			self._source.data = self.data_view.to_dict(orient='list')
		except AttributeError:
			self._source = self.column_data_source(self.data_view)

	def set_view_range(self, event) -> None:
		_start = pandas.to_datetime(self.figure.x_range.start, unit="ms")
		_end = pandas.to_datetime(self.figure.x_range.end, unit="ms")
		_mask = (self.data_view['datetime'] >= _start) & (self.data_view['datetime'] <= _end)
		_min = self.data_view.loc[_mask]['low'].min()
		_max = self.data_view.loc[_mask]['high'].max()
		self.figure.y_range.start = _min
		self.figure.y_range.end = _max
