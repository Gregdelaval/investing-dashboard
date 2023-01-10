import pandas
from bokeh import plotting, models, events
from typing import List, Dict, Callable, Tuple, Union, Type
from ..helpers.helpers import Helpers


class BaseEventHandler():
	log = Helpers().get_logger(__name__)

	def __init__(self, *functions) -> None:
		self.functions = functions

	def on_event(self, event) -> None:
		for _function in self.functions:
			_function()

	def on_change(self, attrname, old, new) -> None:
		for _function in self.functions:
			_function()


class BaseModels():
	date_format = '%Y-%m-%d'
	date_time_format = '%Y-%m-%d %H:%M'
	#TODO Set default colors as globals
	primary_color = '#00eeff'
	primary_color_faded = '#00b0bd'
	secondary_color = '#ff8400'
	secondary_color_faded = '#bd6100'

	def __init__(self) -> None:
		pass

	def divider(
		self,
		text: str,
		color: str = 'white',
	) -> models.Div:
		return models.Div(
			text=f'<b>{text}</b>',
			styles={'color': color},
		)

	def pretext(
		self,
		text: str,
		color: str = 'white',
	) -> models.PreText:
		return models.PreText(
			text=f'{text}',
			styles={'color': color},
		)

	def button(
		self,
		*callbacks: Callable,
		label: str,
		event_type: Union[str, Type[events.Event]] = events.ButtonClick,
		**kwargs,
	) -> models.Button:
		widget = models.Button(
			label=label,
			**kwargs,
		)
		widget.on_event(event_type, BaseEventHandler(*callbacks).on_event)
		return widget

	def checkbox_button_group(
		self,
		*callbacks: Callable,
		labels: list,
		**kwargs,
	) -> models.CheckboxButtonGroup:
		widget = models.CheckboxButtonGroup(
			**kwargs,
			labels=labels,
		)
		widget.on_change('active', *callbacks)
		return widget

	def label(self, text_color: str = 'white', **kwargs) -> models.Label:
		return models.Label(
			text_color=text_color,
			**kwargs,
		)

	def define_box_annotation(self, **kwargs) -> models.BoxAnnotation:
		return models.BoxAnnotation(**kwargs)

	def selector(
		self,
		*callbacks: Callable,
		title: str,
		options: List[str],
		value: str = False,
		sort: bool = True,
		styles: Dict[str, str] = {'color': 'white'},
		**kwargs,
	) -> models.Select:
		if sort:
			options = sorted(options)
		if not value:
			value = options[0]
		selector = models.Select(
			value=value,
			options=options,
			styles=styles,
			title=title,
			**kwargs,
		)
		selector.on_change('value', BaseEventHandler(*callbacks).on_change)
		return selector

	def define_toggle(
		self,
		*callbacks: Callable,
		label: str,
		button_type: str = 'light',
		active: bool = False,
		styles: Dict[str, str] = {'color': 'white'},
		**kwargs,
	) -> models.Toggle:
		toggle = models.Toggle(
			label=label,
			button_type=button_type,
			active=active,
			styles=styles,
			**kwargs,
		)
		toggle.on_change('active', BaseEventHandler(*callbacks).on_change)
		return toggle

	def spinner(
		self,
		*callbacks: Callable,
		title: str,
		low: int,
		high: int,
		step: int,
		value: int,
		styles: Dict[str, str] = {'color': 'white'},
	) -> models.Spinner:
		spinner = models.Spinner(
			low=low,
			high=high,
			step=step,
			value=value,
			title=title,
			styles=styles,
		)
		spinner.on_change('value', *callbacks)
		return spinner

	def range_slider(
		self,
		*callbacks: Callable,
		title: str,
		start: float,
		end: float,
		value: Tuple[float, float],
		step: float,
		show_value: bool = False,
		styles: Dict[str, str] = {'color': 'white'},
	) -> models.Slider:
		range_slider = models.RangeSlider(
			start=start,
			end=end,
			value=value,
			step=step,
			show_value=show_value,
			title=title,
			styles=styles,
		)
		range_slider.on_change('value', *callbacks)
		return range_slider

	def table_columns(
		self,
		df: pandas.DataFrame,
		formats: dict = {},
	) -> List[models.TableColumn]:
		'''
		df = pandas data frame to define list of table columns from
		formats = dict of column:models.<formatter>(format='') to apply for formatting
		'''
		columns = []
		for column in df.columns:
			_args = dict(
				field=column,
				title=column,
			)
			if column == 'datetime':
				_args['formatter'] = models.DateFormatter(format=self.date_time_format)
			if column == 'date':
				_args['formatter'] = models.DateFormatter(format=self.date_format)
			if column in formats.keys():
				_args['formatter'] = formats[column]
			table_column = models.TableColumn(**_args)
			columns.append(table_column)
		return columns

	def define_table(
		self,
		source: plotting.ColumnDataSource,
		columns: List[models.TableColumn],
		height: int,
		width: int,
		autosize_mode: str = 'force_fit',
		header_bakground_color: str = 'white',
	) -> models.DataTable:
		table = models.DataTable(
			source=source,
			columns=columns,
			height=height,
			width=width,
			index_position=None,
			autosize_mode=autosize_mode,
			styles={'background-color': header_bakground_color},
		)
		return table

	def column_data_source(
		self,
		df: pandas.DataFrame,
	) -> plotting.ColumnDataSource:
		return plotting.ColumnDataSource(df)

	def define_hover_tool(
		self,
		tooltips: List[Tuple[str, str]] = [],
		formatters: Dict[str, str] = {},
		renderers: List[models.DataRenderer] = [],
		mode: str = 'vline',
		name: str = 'hover_tool',
		**kwargs,
	) -> models.HoverTool:
		hover_tool = models.HoverTool(
			tooltips=tooltips,
			formatters=formatters,
			renderers=renderers,
			name=name,
			mode=mode,
			**kwargs,
		)
		return hover_tool

	def define_bar_chart(
		self,
		source: models.ColumnDataSource,
		x: str,
		chart_width: int,
		chart_height: int,
		width: float = 0.5,
		hover_tool: models.HoverTool = None,
	) -> plotting.figure:
		x_range = source.data[x]
		chart = plotting.figure(
			x_range=x_range,
			width=chart_width,
			height=chart_height,
		)
		chart.vbar(x=x, source=source, width=width)
		chart.yaxis[0].formatter = models.NumeralTickFormatter()
		if hover_tool:
			chart.tools.append(hover_tool)

		return chart

	def define_figure(
		self,
		x_grid_line_color: str = None,
		y_grid_line_color: str = None,
		background_alpha: float = 0.5,
		y_axis_formatter: Type[models.TickFormatter] = models.NumeralTickFormatter(format='0'),
		x_axis_formatter: Type[models.TickFormatter] = models.DatetimeTickFormatter(),
		**kwargs,
	) -> plotting.figure:
		figure = plotting.figure(**kwargs)
		figure.xgrid.grid_line_color = x_grid_line_color
		figure.ygrid.grid_line_color = y_grid_line_color
		figure.background_fill_alpha = background_alpha
		figure.yaxis.formatter = y_axis_formatter
		figure.xaxis.formatter = x_axis_formatter
		return figure

	def define_circle(self, **kwargs) -> models.Circle:
		return models.Circle(**kwargs)

	def define_scatter(self, **kwargs) -> models.Scatter:
		return models.Scatter(**kwargs)

	def define_whisker(self, **kwargs) -> models.Whisker:
		return models.Whisker(**kwargs)

	def define_segment(
		self,
		line_color: str = 'black',
		**kwargs,
	) -> models.Segment:
		return models.Segment(**kwargs, line_color=line_color)

	def define_line(
		self,
		line_color: str = primary_color,
		**kwargs,
	) -> models.Line:
		return models.Line(line_color=line_color, **kwargs)

	def define_vbar(
		self,
		line_color: str = 'black',
		**kwargs,
	):
		return models.VBar(
			**kwargs,
			line_color=line_color,
		)
