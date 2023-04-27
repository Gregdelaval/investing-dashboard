from .base import BaseView, BaseController, BaseModel
from bokeh import models, events, plotting, palettes
from bokeh.layouts import gridplot, column, row
import pandas
import numpy
from typing import List, Dict
from typing import Callable


class PortfolioView(BaseView):

	def __init__(
		self,
		logger_name,
		instrument_plot_width,
		instrument_plot_height,
		sector_table_width,
		sector_table_height,
		panel_title,
	) -> None:
		super().__init__(logger_name=logger_name)
		#Tools
		self._sector_exposure_hover_tool = models.HoverTool()
		self._country_exposure_hover_tool = models.HoverTool()
		self._instrument_exposure_hover_tool = models.HoverTool()

		#Figures
		self._instrument_plot = plotting.figure(
			x_axis_type='datetime',
			active_scroll='wheel_zoom',
			width=instrument_plot_width,
			height=instrument_plot_height,
			background_fill_alpha=0.5,
			x_range=[0, 1],
			y_range=[0, 1],
		)
		self.instrument_plot.yaxis.major_label_text_color = "white"
		self.instrument_plot.xaxis.major_label_text_color = "white"
		self.instrument_plot.xgrid.grid_line_color = None
		self.instrument_plot.ygrid.grid_line_color = None
		self.instrument_plot.yaxis.formatter = models.NumeralTickFormatter(format='0')
		self.instrument_plot.xaxis.formatter = models.DatetimeTickFormatter()

		self._sector_exposure_chart = plotting.figure(
			title='Sector Exposure',
			width=sector_table_width,
			height=sector_table_height,
			background_fill_alpha=0.5,
			x_range=models.Range1d(0, 1, bounds="auto"),
			y_range=models.Range1d(-1, 1, bounds="auto"),
		)
		self.sector_exposure_chart.title.text_color = 'white'
		self.sector_exposure_chart.yaxis[0].formatter = models.CustomJSTickFormatter(
			code="""return tick + " % " """
		)
		self.sector_exposure_chart.ygrid.grid_line_color = None
		self.sector_exposure_chart.yaxis.major_label_text_color = "white"
		self.sector_exposure_chart.xaxis.major_label_text_color = "white"
		self.sector_exposure_chart.xaxis.major_label_orientation = 45 * (3.14159265 / 180)
		self.sector_exposure_chart.add_tools(self.sector_exposure_hover_tool)

		self._country_exposure_chart = plotting.figure(
			title='Country Exposure',
			width=sector_table_width,
			height=sector_table_height,
			background_fill_alpha=0.5,
			x_range=models.Range1d(0, 1, bounds="auto"),
			y_range=models.Range1d(-1, 1, bounds="auto"),
		)
		self.country_exposure_chart.title.text_color = 'white'
		self.country_exposure_chart.yaxis[0].formatter = models.CustomJSTickFormatter(
			code="""return tick + " % " """
		)
		self.country_exposure_chart.ygrid.grid_line_color = None
		self.country_exposure_chart.yaxis.major_label_text_color = "white"
		self.country_exposure_chart.xaxis.major_label_text_color = "white"
		self.country_exposure_chart.xaxis.major_label_orientation = 45 * (3.14159265 / 180)
		self.country_exposure_chart.add_tools(self.country_exposure_hover_tool)

		self._instrument_exposure_chart = plotting.figure(
			title='Real Instrument Exposure',
			width=sector_table_width,
			height=sector_table_height,
			background_fill_alpha=0.5,
			x_range=models.Range1d(0, 1, bounds="auto"),
			y_range=models.Range1d(-1, 1, bounds="auto"),
		)
		self.instrument_exposure_chart.title.text_color = 'white'
		self.instrument_exposure_chart.yaxis[0].formatter = models.CustomJSTickFormatter(
			code="""return tick + " % " """
		)
		self.instrument_exposure_chart.ygrid.grid_line_color = None
		self.instrument_exposure_chart.yaxis.major_label_text_color = "white"
		self.instrument_exposure_chart.xaxis.major_label_text_color = "white"
		self.instrument_exposure_chart.xaxis.major_label_orientation = 45 * (3.14159265 / 180)
		self.instrument_exposure_chart.add_tools(self.instrument_exposure_hover_tool)

		#Controllers
		self._positions_calculation_button = models.Button(label='Update insights')
		self._positions_scale_toggle = models.Toggle(label='Scale to used credit')
		self._plot_calculation_button = models.Button(label='Update plot')
		self._instrument_selector = models.Select(title='Instrument', value=None)
		self._granularity_selector = models.Select(title='Granularity', value=None)
		self._open_orders_toggle = models.Toggle(label='Open Orders')
		self._closed_positions_toggle = models.Toggle(label='Closed Pos.')
		self._open_positions_toggle = models.Toggle(label='Open Pos.')

		#Labels and separators
		self._instrument_plot_controllers_header = models.Div(text='INSTRUMENT PLOT')
		self._portfolio_insights_controllers_header = models.Div(text='PORTFOLIO INSIGHTS')
		_widgets_column_segment_1_height = 300
		_separator = models.Div(height=instrument_plot_height - _widgets_column_segment_1_height)

		#Panel
		_widgets_column_segment_1 = self.fit_column_content(
			column_width=300,
			content=column(
			row(self.instrument_plot_controllers_header),
			row(self.instrument_selector, self.granularity_selector),
			row(self.open_positions_toggle, self.closed_positions_toggle, self.open_orders_toggle),
			row(self.plot_calculation_button),
			height=_widgets_column_segment_1_height,
			)
		)
		_widgets_column_segment_2 = self.fit_column_content(
			column_width=300,
			content=column(
			self.portfolio_insights_controllers_header,
			self.positions_calculation_button,
			self.positions_scale_toggle,
			)
		)
		_plots_column = self.fit_column_content(
			column_width=instrument_plot_width,
			content=column(
			row(self.instrument_plot),
			row(self.instrument_exposure_chart, self.country_exposure_chart),
			row(self.sector_exposure_chart),
			)
		)
		self._layout = gridplot(
			toolbar_location='left',
			merge_tools=True,
			toolbar_options=dict(logo=None),
			children=[[
			column(
			_widgets_column_segment_1,
			_separator,
			_widgets_column_segment_2,
			),
			_plots_column,
			]]
		)
		self._panel = models.TabPanel(
			child=self.layout,
			title=panel_title,
		)

		#Glyphs
		self._instrument_exposure_vbar_glyph = models.VBar(
			width=0.9,
			fill_color='#00eeff',
		)
		self._country_exposure_vbar_glyph = models.VBar(
			width=0.9,
			fill_color='#00eeff',
		)
		self._sector_exposure_vbar_glyph = models.VBar(
			width=0.9,
			fill_color='#00eeff',
		)
		self._open_orders_opening_glyph = models.Segment(
			x0='start_index',
			x1='end_index',
			y0='rate',
			y1='rate',
			line_color='position_type_color',
			line_alpha=0.7,
			tags=['open_orders_glyph'],
		)
		self._closed_position_closing_glyph = models.Scatter(
			x='close_index',
			y='close_rate',
			marker='circle',
			fill_color='closing_color',
			fill_alpha=0.5,
			line_alpha=0,
			tags=['closed_position_glyph'],
		)
		self._closed_positions_opening_glyph = models.Scatter(
			x='open_index',
			y='open_rate',
			marker='marker',
			fill_color='gray',
			tags=['closed_position_glyph'],
			size=10,
		)
		self._closed_position_connector_glyph = models.Segment(
			x0='open_index',
			y0='open_rate',
			x1='close_index',
			y1='close_rate',
			line_color='closing_color',
			line_alpha=0.5,
			tags=['closed_position_glyph'],
		)
		self._stop_loss_vline_glyph = models.Segment(
			x0='index',
			y0='open_rate',
			x1='index',
			y1='stop_loss_rate',
			line_color='red',
			line_alpha=0.5,
			tags=['open_position_glyph'],
		)
		self._stop_loss_hline_glyph = models.Block(
			x='index',
			y='stop_loss_rate',
			line_color='red',
			width=3,
			height=1,
			line_alpha=0.5,
			tags=['open_position_glyph'],
		)
		self._take_profit_vline_glyph = models.Segment(
			x0='index',
			y0='open_rate',
			x1='index',
			y1='take_profit_rate',
			line_color='green',
			line_alpha=0.5,
			tags=['open_position_glyph'],
		)
		self._take_profit_hline_glyph = models.Block(
			x='index',
			y='take_profit_rate',
			line_color='green',
			width=3,
			height=1,
			line_alpha=0.5,
			tags=['open_position_glyph'],
		)
		self._open_positions_glyph = models.Scatter(
			x='index',
			y='open_rate',
			marker='marker',
			fill_color='turquoise',
			size=10,
			tags=['open_position_glyph'],
		)
		self._ohlc_line_glyph = models.Segment(
			x0='index',
			y0='high',
			x1='index',
			y1='low',
			line_color='black',
		)
		self._ohlc_bar_glyph = models.VBar(
			x='index',
			top='open',
			bottom='close',
			fill_color='color',
			line_color='black',
			width=0.5,
		)

	@property
	def country_exposure_chart(self):
		return self._country_exposure_chart

	@property
	def country_exposure_hover_tool(self):
		return self._country_exposure_hover_tool

	@property
	def country_exposure_vbar_glyph(self):
		return self._country_exposure_vbar_glyph

	@property
	def instrument_exposure_chart(self):
		return self._instrument_exposure_chart

	@property
	def instrument_exposure_hover_tool(self):
		return self._instrument_exposure_hover_tool

	@property
	def instrument_exposure_vbar_glyph(self):
		return self._instrument_exposure_vbar_glyph

	@property
	def sector_exposure_chart(self):
		return self._sector_exposure_chart

	@property
	def sector_exposure_hover_tool(self):
		return self._sector_exposure_hover_tool

	@property
	def sector_exposure_vbar_glyph(self):
		return self._sector_exposure_vbar_glyph

	@property
	def closed_position_closing_glyph(self):
		return self._closed_position_closing_glyph

	@property
	def closed_position_connector_glyph(self):
		return self._closed_position_connector_glyph

	@property
	def closed_positions_opening_glyph(self):
		return self._closed_positions_opening_glyph

	@property
	def instrument_plot(self):
		return self._instrument_plot

	@property
	def ohlc_bar_glyph(self):
		return self._ohlc_bar_glyph

	@property
	def ohlc_line_glyph(self):
		return self._ohlc_line_glyph

	@property
	def open_positions_glyph(self):
		return self._open_positions_glyph

	@property
	def stop_loss_hline_glyph(self):
		return self._stop_loss_hline_glyph

	@property
	def stop_loss_vline_glyph(self):
		return self._stop_loss_vline_glyph

	@property
	def take_profit_hline_glyph(self):
		return self._take_profit_hline_glyph

	@property
	def take_profit_vline_glyph(self):
		return self._take_profit_vline_glyph

	@property
	def closed_positions_toggle(self):
		return self._closed_positions_toggle

	@property
	def granularity_selector(self):
		return self._granularity_selector

	@property
	def instrument_plot_controllers_header(self):
		return self._instrument_plot_controllers_header

	@property
	def instrument_selector(self):
		return self._instrument_selector

	@property
	def layout(self):
		return self._layout

	@property
	def open_orders_toggle(self):
		return self._open_orders_toggle

	@property
	def open_orders_opening_glyph(self):
		return self._open_orders_opening_glyph

	@property
	def open_positions_toggle(self):
		return self._open_positions_toggle

	@property
	def panel(self):
		return self._panel

	@property
	def plot_calculation_button(self):
		return self._plot_calculation_button

	@property
	def portfolio_insights_controllers_header(self):
		return self._portfolio_insights_controllers_header

	@property
	def positions_calculation_button(self):
		return self._positions_calculation_button

	@property
	def positions_scale_toggle(self):
		return self._positions_scale_toggle

	@property
	def separator(self):
		return self._separator


class PortfolioModel(BaseModel):

	def __init__(self, logger_name) -> None:
		super().__init__(logger_name)
		self._portfolio_overview = self.fetch_portfolio_overview()
		self._instrument_granularities = {
			'5m': '%Y-%m-%d %H:%M',
			'1h': '%Y-%m-%d %H',
			'1d': '%Y-%m-%d',
			'1wk': '%Y-%m-%d',
			'1mo': '%Y-%m',
		}

		self._instrument_data = pandas.DataFrame()
		self._instrument_cds = plotting.ColumnDataSource(self._instrument_data)

		self._open_positions_data_set = pandas.DataFrame()
		self._open_positions_data_view = pandas.DataFrame()
		self._open_positions_cds = plotting.ColumnDataSource(self._open_positions_data_view)

		self._closed_positions_data_set = pandas.DataFrame()
		self._closed_positions_data_view = pandas.DataFrame()
		self._closed_positions_cds = plotting.ColumnDataSource(self._closed_positions_data_view)

		self._open_orders_data_set = pandas.DataFrame()
		self._open_orders_data_view = pandas.DataFrame()
		self._open_orders_cds = plotting.ColumnDataSource(self._open_orders_data_view)

		self._sector_exposure_data_set = pandas.DataFrame()
		self._sector_exposure_data_view = pandas.DataFrame()
		self._sector_exposure_cds = plotting.ColumnDataSource(self._sector_exposure_data_view)

		self._country_exposure_data_set = pandas.DataFrame()
		self._country_exposure_data_view = pandas.DataFrame()
		self._country_exposure_cds = plotting.ColumnDataSource(self._country_exposure_data_view)

		self._instrument_exposure_data_set = pandas.DataFrame()
		self._instrument_exposure_data_view = pandas.DataFrame()
		self._instrument_exposure_cds = plotting.ColumnDataSource(self._instrument_exposure_data_view)

	@property
	def instrument_exposure_cds(self) -> plotting.ColumnDataSource:
		return self._instrument_exposure_cds

	@property
	def instrument_exposure_data_view(self) -> pandas.DataFrame:
		return self._instrument_exposure_data_view

	@instrument_exposure_data_view.setter
	def instrument_exposure_data_view(self, df: pandas.DataFrame):
		self._instrument_exposure_data_view = df

	@property
	def instrument_exposure_data_set(self) -> pandas.DataFrame:
		return self._instrument_exposure_data_set

	@instrument_exposure_data_set.setter
	def instrument_exposure_data_set(self, df: pandas.DataFrame):
		self._instrument_exposure_data_set = df

	@property
	def country_exposure_cds(self) -> plotting.ColumnDataSource:
		return self._country_exposure_cds

	@property
	def country_exposure_data_view(self) -> pandas.DataFrame:
		return self._country_exposure_data_view

	@country_exposure_data_view.setter
	def country_exposure_data_view(self, df: pandas.DataFrame):
		self._country_exposure_data_view = df

	@property
	def country_exposure_data_set(self) -> pandas.DataFrame:
		return self._country_exposure_data_set

	@country_exposure_data_set.setter
	def country_exposure_data_set(self, df: pandas.DataFrame):
		self._country_exposure_data_set = df

	@property
	def sector_exposure_cds(self) -> plotting.ColumnDataSource:
		return self._sector_exposure_cds

	@property
	def sector_exposure_data_view(self) -> pandas.DataFrame:
		return self._sector_exposure_data_view

	@sector_exposure_data_view.setter
	def sector_exposure_data_view(self, df: pandas.DataFrame):
		self._sector_exposure_data_view = df

	@property
	def sector_exposure_data_set(self) -> pandas.DataFrame:
		return self._sector_exposure_data_set

	@sector_exposure_data_set.setter
	def sector_exposure_data_set(self, df: pandas.DataFrame):
		self._sector_exposure_data_set = df

	@property
	def open_orders_data_set(self) -> pandas.DataFrame:
		return self._open_orders_data_set

	@open_orders_data_set.setter
	def open_orders_data_set(self, df: pandas.DataFrame):
		assert isinstance(df, pandas.DataFrame), 'Passed object is not a DF'
		df['position_type_color'] = numpy.select(
			[df['is_buy'] == 1, df['is_buy'] == 0],
			['green', 'red'],
		)

		self._open_orders_data_set = df

	@property
	def open_orders_data_view(self) -> pandas.DataFrame:
		return self._open_orders_data_view

	@open_orders_data_view.setter
	def open_orders_data_view(self, df: pandas.DataFrame) -> pandas.DataFrame:
		self._open_orders_data_view = df

	@property
	def open_orders_cds(self) -> plotting.ColumnDataSource:
		return self._open_orders_cds

	@property
	def closed_positions_data_set(self) -> pandas.DataFrame:
		return self._closed_positions_data_set

	@closed_positions_data_set.setter
	def closed_positions_data_set(self, df: pandas.DataFrame):  #closing_color
		assert isinstance(df, pandas.DataFrame), 'Passed object is not a DF'
		df['marker'] = numpy.select(
			[df['is_buy'] == 1, df['is_buy'] == 0],
			['triangle', 'inverted_triangle'],
		)
		df['closing_color'] = numpy.select(
			[df['net_profit'] > 0, df['net_profit'] < 0],
			['green', 'red'],
		)
		self._closed_positions_data_set = df

	@property
	def closed_positions_data_view(self) -> pandas.DataFrame:
		return self._closed_positions_data_view

	@closed_positions_data_view.setter
	def closed_positions_data_view(self, df: pandas.DataFrame) -> pandas.DataFrame:
		self._closed_positions_data_view = df

	@property
	def closed_positions_cds(self) -> plotting.ColumnDataSource:
		return self._closed_positions_cds

	@property
	def open_positions_data_set(self) -> pandas.DataFrame:
		return self._open_positions_data_set

	@open_positions_data_set.setter
	def open_positions_data_set(self, df: pandas.DataFrame):
		assert isinstance(df, pandas.DataFrame), 'Passed object is not a DF'
		df['marker'] = numpy.select(
			[df['is_buy'] == 1, df['is_buy'] == 0],
			['triangle', 'inverted_triangle'],
		)

		self._open_positions_data_set = df

	@property
	def open_positions_data_view(self) -> pandas.DataFrame:
		return self._open_positions_data_view

	@open_positions_data_view.setter
	def open_positions_data_view(self, df: pandas.DataFrame) -> pandas.DataFrame:
		self._open_positions_data_view = df

	@property
	def open_positions_cds(self) -> plotting.ColumnDataSource:
		return self._open_positions_cds

	@property
	def instrument_cds(self) -> plotting.ColumnDataSource:
		return self._instrument_cds

	@property
	def instrument_data(self) -> pandas.DataFrame:
		return self._instrument_data

	@instrument_data.setter
	def instrument_data(self, df):
		assert isinstance(df, pandas.DataFrame), 'Passed object is not a DF'
		df['change'] = (df['close'] - df['close'].shift(1)) / df['close'].shift(1) * 100
		df['color'] = numpy.select([df['change'] > 0, df['change'] < 0], ['green', 'red'])
		df.reset_index(inplace=True)
		self._instrument_data = df

	@property
	def portfolio_overview(self) -> pandas.DataFrame:
		return self._portfolio_overview

	def portfolio_overview_etoro_symbols(self) -> List[str]:
		return self.portfolio_overview['etoro_symbol_name'].values.tolist()

	def common_symbol_lookup(self, etoro_symbol: str) -> str:
		_df = self.portfolio_overview
		return _df.loc[_df['etoro_symbol_name'] == etoro_symbol]['common_name'].values[0]

	@property
	def instrument_granularities(self) -> Dict[str, str]:
		return self._instrument_granularities

	def instrument_granularities_list(self) -> List[str]:
		return list(self.instrument_granularities)


class Portfolio(PortfolioView, PortfolioModel, BaseController):

	def __init__(self) -> None:
		super().__init__(
			logger_name=__name__,
			instrument_plot_width=1280,
			instrument_plot_height=720,
			sector_table_height=360,
			sector_table_width=640,
			panel_title='Portfolio',
		)

		self.instrument_selector.options = self.portfolio_overview_etoro_symbols()
		self.instrument_selector.value = self.instrument_selector.options[0]
		self.granularity_selector.options = self.instrument_granularities_list()
		self.granularity_selector.value = self.granularity_selector.options[0]

		self.append_callback(model=self.plot_calculation_button, function=self.update_instrument_plot)
		self.append_callback(model=self.plot_calculation_button, function=self.update_view_range, x_min=180, x_max=5) # Yapf:disable
		self.append_callback(model=self.plot_calculation_button, function=self.update_open_positions)
		self.append_callback(model=self.plot_calculation_button, function=self.update_closed_positions)
		self.append_callback(model=self.plot_calculation_button, function=self.update_open_orders)
		self.append_callback(model=self.open_positions_toggle, function=self.update_open_positions)
		self.append_callback(model=self.closed_positions_toggle, function=self.update_closed_positions)
		self.append_callback(model=self.open_orders_toggle, function=self.update_open_orders)
		self.append_callback(model=self.instrument_plot, function=self.update_view_range, event_type=events.MouseWheel) # Yapf:disable
		self.append_callback(model=self.positions_calculation_button, function=self.update_insights_tables) # Yapf:disable
		self.append_callback(model=self.positions_scale_toggle, function=self.update_insights_tables) # Yapf:disable


	@BaseController.log_call
	def update_insights_tables(self):

		def update_table(aggregate: str):
			#Define variables
			fetch_data_func = getattr(self, f'fetch_{aggregate}_exposure_data')
			data_set_attr = f'{aggregate}_exposure_data_set'
			data_view_attr = f'{aggregate}_exposure_data_view'
			cds_attr = f'{aggregate}_exposure_cds'
			chart_attr = f'{aggregate}_exposure_chart'
			glyph_attr = f'{aggregate}_exposure_vbar_glyph'
			hover_tool_attr = f'{aggregate}_exposure_hover_tool'

			if self.positions_scale_toggle.active:
				column_name = f'scaled_{aggregate}_exposure'
			else:
				column_name = f'{aggregate}_exposure'

			# Set data
			data_set: pandas.DataFrame = getattr(self, data_set_attr)
			if data_set.empty:
				data_set = fetch_data_func()

			data_view: pandas.DataFrame = getattr(self, data_view_attr)
			data_view = data_set
			data_view.sort_values(by=column_name, ascending=False, inplace=True, ignore_index=True)
			data_view['index'] = data_view.reset_index().index

			# Update data source
			getattr(self, cds_attr).data.update(data_view)

			# Update chart range
			chart: plotting.Figure = getattr(self, chart_attr)
			chart.x_range.start = data_view.index.min() - 0.5
			chart.x_range.end = data_view.index.max() + 0.5
			chart.y_range.start = data_view[column_name].min()
			chart.y_range.end = data_view[column_name].max()

			# Update chart glyphs and axis
			color_mapper = models.CategoricalColorMapper(
				factors=data_view[aggregate].unique().tolist(),
				palette=numpy.array(palettes.Plasma256)\
  [numpy.linspace(0, 255, len(data_view[aggregate].unique()),dtype=int)].tolist(),
			)

			vbar_glyph = getattr(self, glyph_attr)
			vbar_glyph.top = column_name
			vbar_glyph.bottom = 0
			vbar_glyph.x = 'index'
			vbar_glyph.fill_color = {
				'field': aggregate,
				'transform': color_mapper,
			}

			if len(chart.select({'id': vbar_glyph.id})) == 0:
				chart.add_glyph(getattr(self, cds_attr), vbar_glyph)
			chart.xaxis.major_label_overrides = data_view[aggregate].to_dict()
			chart.xaxis.ticker = models.FixedTicker(ticks=data_view['index'].tolist())

			# Update hover tooltips
			getattr(self, hover_tool_attr).tooltips = [
				(aggregate, f'@{aggregate}'),
				('Exposure', f'@{column_name} %'),
			]

		# Update model components
		update_table(aggregate='sector')
		update_table(aggregate='instrument')
		update_table(aggregate='country')

	@BaseController.log_call
	def update_instrument_plot(self):
		#Read state
		granularity = self.granularity_selector.value
		instrument = self.common_symbol_lookup(self.instrument_selector.value)

		#Update model components
		self.instrument_data = self.fetch_instrument_data(instrument=instrument, granularity=granularity)
		self.instrument_cds.data.update(self.instrument_data)

		#Update view components
		if len(self.instrument_plot.select({'id': self.ohlc_line_glyph.id})) == 0:
			self.instrument_plot.add_glyph(self.instrument_cds, self.ohlc_line_glyph)
			self.instrument_plot.add_glyph(self.instrument_cds, self.ohlc_bar_glyph)

		self.instrument_plot.xaxis.major_label_overrides = self.instrument_data['datetime'].dt.strftime(
			self.instrument_granularities[granularity]
		).to_dict()

	@BaseController.log_call
	def update_open_positions(self):
		if self.open_positions_toggle.active == True:
			#Update model components
			if self.open_positions_data_set.empty:
				self.open_positions_data_set = self.fetch_portfolio_open_positions()

			self.open_positions_data_view = self.open_positions_data_set
			self.open_positions_data_view = self.filter_data_frame(
				df=self.open_positions_data_view,
				column='symbol_full',
				value=self.instrument_selector.value,
			)
			self.open_positions_data_view = self.inherit_closest_index(
				parent_df=self.instrument_data,
				parent_on='datetime',
				child_df=self.open_positions_data_view,
				child_on='open_date_time',
			)
			self.open_positions_cds.data.update(self.open_positions_data_view)

			#Update view components
			if len(self.instrument_plot.select({'id': self.open_positions_glyph.id})) == 0:
				self.instrument_plot.add_glyph(self.open_positions_cds, self.open_positions_glyph)
				self.instrument_plot.add_glyph(self.open_positions_cds, self.take_profit_hline_glyph)
				self.instrument_plot.add_glyph(self.open_positions_cds, self.take_profit_vline_glyph)
				self.instrument_plot.add_glyph(self.open_positions_cds, self.stop_loss_hline_glyph)
				self.instrument_plot.add_glyph(self.open_positions_cds, self.stop_loss_vline_glyph)

			self.toggle_renderers_based_on_tag(
				model=self.instrument_plot,
				tags=['open_position_glyph'],
				visible=True,
			)
		else:
			#Update view components
			self.toggle_renderers_based_on_tag(
				model=self.instrument_plot,
				tags=['open_position_glyph'],
				visible=False,
			)

	@BaseController.log_call
	def update_closed_positions(self):
		if self.closed_positions_toggle.active == True:
			#Update model components
			if self.closed_positions_data_set.empty:
				self.closed_positions_data_set = self.fetch_portfolio_closed_positions()

			self.closed_positions_data_view = self.closed_positions_data_set
			self.closed_positions_data_view = self.filter_data_frame(
				df=self.closed_positions_data_view,
				column='symbol_full',
				value=self.instrument_selector.value,
			)

			self.closed_positions_data_view = self.inherit_closest_index(
				parent_df=self.instrument_data,
				parent_on='datetime',
				child_df=self.closed_positions_data_view,
				child_on='close_date_time',
			)
			self.closed_positions_data_view = self.closed_positions_data_view.rename(
				columns={'index': 'close_index'}
			)

			self.closed_positions_data_view = self.inherit_closest_index(
				parent_df=self.instrument_data,
				parent_on='datetime',
				child_df=self.closed_positions_data_view,
				child_on='open_date_time',
			)
			self.closed_positions_data_view = self.closed_positions_data_view.rename(
				columns={'index': 'open_index'}
			)

			self.closed_positions_data_view = self.closed_positions_data_view.reset_index()
			self.closed_positions_cds.data.update(self.closed_positions_data_view)

			#Update view components
			if len(self.instrument_plot.select({'id': self.closed_position_closing_glyph.id})) == 0:
				self.instrument_plot.add_glyph(self.closed_positions_cds, self.closed_position_closing_glyph)
				self.instrument_plot.add_glyph(self.closed_positions_cds, self.closed_positions_opening_glyph)
				self.instrument_plot.add_glyph(self.closed_positions_cds, self.closed_position_connector_glyph)

			self.toggle_renderers_based_on_tag(
				model=self.instrument_plot, tags=['closed_position_glyph'], visible=True
			)
		else:
			#Update view components
			self.toggle_renderers_based_on_tag(
				model=self.instrument_plot, tags=['closed_position_glyph'], visible=False
			)

	@BaseController.log_call
	def update_open_orders(self):
		if self.open_orders_toggle.active == True:
			#Update model components
			if self.open_orders_data_set.empty:
				self.open_orders_data_set = self.fetch_portfolio_open_orders()

			self.open_orders_data_view = self.open_orders_data_set
			self.open_orders_data_view = self.filter_data_frame(
				df=self.open_orders_data_view,
				column='symbol_full',
				value=self.instrument_selector.value,
			)
			self.open_orders_data_view = self.open_orders_data_view.reset_index()
			self.open_orders_data_view['start_index'] = self.instrument_data.index.max()
			self.open_orders_data_view['end_index'] = 99999
			self.open_orders_cds.data.update(self.open_orders_data_view)

			#Update view components
			if len(self.instrument_plot.select({'id': self.open_orders_opening_glyph.id})) == 0:
				self.instrument_plot.add_glyph(self.open_orders_cds, self.open_orders_opening_glyph)

			self.toggle_renderers_based_on_tag(
				model=self.instrument_plot, tags=['open_orders_glyph'], visible=True
			)
		else:
			#Update view components
			self.toggle_renderers_based_on_tag(
				model=self.instrument_plot, tags=['open_orders_glyph'], visible=False
			)

	def update_view_range(self, x_min: int = None, x_max: int = None):

		_df = self.instrument_data

		#X-axis
		if x_min:
			_x_range_min = _df.index.max() - x_min
			self.instrument_plot.x_range.start = _x_range_min
		else:
			_x_range_min = self.instrument_plot.x_range.start
		if x_max:
			_x_range_max = _df.index.max() + x_max
			self.instrument_plot.x_range.end = _x_range_max
		else:
			_x_range_max = self.instrument_plot.x_range.end

		#Y-axis
		_mask = (_df.index >= _x_range_min) & (_df.index <= _x_range_max)
		self.instrument_plot.y_range.start = _df.loc[_mask]['low'].min()
		self.instrument_plot.y_range.end = _df.loc[_mask]['high'].max()
