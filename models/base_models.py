import pandas
from bokeh import plotting, models
from typing import List, Dict, Callable, Tuple
from bokeh.core.enums import MarkerType


class BaseModels():
	date_format = '%Y-%m-%d'
	date_time_format = '%Y-%m-%d %H:%M'

	def __init__(self) -> None:
		pass

	def divider(
		self,
		text: str,
		color: str = 'white',
	) -> models.Div:
		return models.Div(
			text=f'<b>{text}</b>',
			style={'color': color},
		)

	def pretext(
		self,
		text: str,
		color: str = 'white',
	) -> models.PreText:
		return models.PreText(
			text=f'{text}',
			style={'color': color},
		)

	def button(
		self,
		*callbacks: Callable,
		label: str,
		**kwargs,
	) -> models.Button:
		widget = models.Button(
			label=label,
			**kwargs,
		)
		widget.on_click(*callbacks)
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
		options: List[str],
		sort: bool = True,
	) -> models.Select:
		if sort:
			options = sorted(options)
		selector = models.Select(
			value=options[0],
			options=options,
		)
		selector.on_change('value', *callbacks)
		return selector

	def define_toggle(
		self,
		*callbacks: Callable,
		label: str,
		button_type: str = 'light',
		**kwargs,
	) -> models.Toggle:
		toggle = models.Toggle(
			label=label,
			button_type=button_type,
			**kwargs,
		)
		toggle.on_change('active', *callbacks)
		return toggle

	def spinner(
		self,
		*callbacks: Callable,
		low: int,
		high: int,
		step: int,
		value: int,
	) -> models.Spinner:
		spinner = models.Spinner(
			low=low,
			high=high,
			step=step,
			value=value,
		)
		spinner.on_change('value', *callbacks)
		return spinner

	def range_slider(
		self,
		*callbacks: Callable,
		start: float,
		end: float,
		value: Tuple[float, float],
		step: float,
		show_value: bool = False,
	) -> models.Slider:
		range_slider = models.RangeSlider(
			start=start,
			end=end,
			value=value,
			step=step,
			show_value=show_value,
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
	) -> models.DataTable:
		table = models.DataTable(
			source=source,
			columns=columns,
			height=400,
			index_position=None,
			autosize_mode='fit_columns',
		)
		return table

	def column_data_source(
		self,
		df: pandas.DataFrame,
	) -> plotting.ColumnDataSource:
		return plotting.ColumnDataSource(df)

	def define_hover_tool(
		self,
		tooltips: List[Tuple[str, str]],
		formatters: Dict[str, str] = {},
		names: List[str] = [],
		mode: str = 'vline',
		name: str = 'hover_tool',
		**kwargs,
	) -> models.HoverTool:
		hover_tool = models.HoverTool(
			tooltips=tooltips,
			formatters=formatters,
			names=names,
			name=name,
			mode=mode,
			**kwargs,
		)
		return hover_tool

	def define_bar_chart(
		self,
		source: models.ColumnDataSource,
		x: str,
		width: float = 0.5,
		hover_tool: models.HoverTool = None,
	) -> plotting.figure:
		x_range = source.data[x]
		chart = plotting.figure(x_range=x_range)
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
		**kwargs,
	) -> plotting.Figure:
		figure = plotting.figure(**kwargs)
		figure.xgrid.grid_line_color = x_grid_line_color
		figure.ygrid.grid_line_color = y_grid_line_color
		figure.background_fill_alpha = background_alpha
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

	def define_vbar(
		self,
		line_color: str = 'black',
		**kwargs,
	):
		return models.VBar(
			**kwargs,
			line_color=line_color,
		)
