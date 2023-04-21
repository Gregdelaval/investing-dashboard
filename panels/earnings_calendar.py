from .base import BaseView, BaseController, BaseModel
from bokeh import models
from bokeh.layouts import gridplot, column, row
import pandas
from typing import List


class EarningsCalendarView(BaseView):

	def __init__(
		self,
		logger_name,
		chart_width,
		chart_height,
		panel_title,
	) -> None:
		super().__init__(logger_name=logger_name)
		#Table
		self.table = models.DataTable(
			width=chart_width,
			height=chart_height,
			index_position=None,
			autosize_mode='force_fit',
			styles={
			'background-color': 'white',
			'color': 'black',
			},
		)

		#Controllers
		self._index_selector = models.Select(title='Filter for index', value=None)
		self._number_of_companies_input = models.NumericInput(
			title='Include top # of companies',
			low=1,
			high=500,
			value=None,
		)
		self._update_table_button = models.Button(label='Update')

		#Panel
		_widgets_column = self.fit_column_content(
			column_width=300,
			content=column(
			row(
			self.index_selector,
			self.number_of_companies_input,
			),
			self.update_table_button,
			)
		)
		self._layout = gridplot(
			toolbar_location='left',
			merge_tools=True,
			toolbar_options=dict(logo=None),
			children=[[
			_widgets_column,
			self.table,
			]]
		)
		self._panel = models.TabPanel(
			child=self.layout,
			title=panel_title,
		)

	@property
	def update_table_button(self):
		return self._update_table_button

	@property
	def number_of_companies_input(self):
		return self._number_of_companies_input

	@property
	def index_selector(self):
		return self._index_selector

	@property
	def panel(self):
		return self._panel

	@property
	def layout(self):
		return self._layout


class EarningsCalendarModel(BaseModel):

	def __init__(self, logger_name) -> None:
		super().__init__(logger_name=logger_name)

		self._available_indices_data_set = pandas.DataFrame()

		self._constituents_data_set = pandas.DataFrame()

		self._earnings_data_set = pandas.DataFrame()
		self._earnings_data_view = pandas.DataFrame()
		self._columns = [models.TableColumn, ...]
		self._cds = models.ColumnDataSource(self._earnings_data_view)

	@property
	def available_indices_data_set(self):
		return self._available_indices_data_set

	@available_indices_data_set.setter
	def available_indices_data_set(self, df: pandas.DataFrame):
		self._available_indices_data_set = df

	@property
	def cds(self):
		return self._cds

	@property
	def columns(self):
		return self._columns

	@columns.setter
	def columns(self, df: pandas.DataFrame):
		_columns = []
		for column in df.columns:
			_args = dict(field=column, title=column)
			if column in ['date', 'fiscal_date_ending', 'updated_from_date']:
				_args['formatter'] = models.DateFormatter(format='%Y-%m-%d')
			_columns.append(models.TableColumn(**_args))

		self._columns = _columns

	@property
	def earnings_data_view(self):
		return self._earnings_data_view

	@earnings_data_view.setter
	def earnings_data_view(self, df):
		self._earnings_data_view = df

	@property
	def earnings_data_set(self):
		return self._earnings_data_set

	@earnings_data_set.setter
	def earnings_data_set(self, df):
		self._earnings_data_set = df

	@property
	def constituents_data_set(self):
		return self._constituents_data_set

	def constituents_available_indices(self, df: pandas.DataFrame) -> List[str]:
		return df['index_name'].unique().tolist()

	@constituents_data_set.setter
	def constituents_data_set(self, df):
		self._constituents_data_set = df


class EarningsCalendar(EarningsCalendarView, EarningsCalendarModel, BaseController):

	def __init__(self) -> None:
		super().__init__(
			logger_name=__name__,
			chart_width=16 * 50,
			chart_height=9 * 50,
			panel_title='Earnings Calendar',
		)
		self.available_indices_data_set = self.fetch_available_index_constituents()

		self.index_selector.options = self.available_indices_data_set['common_name'].tolist()
		self.index_selector.value = self.index_selector.options[0]

		self.append_callback(model=self.index_selector, function=self.update_number_of_companies_input)
		self.append_callback(model=self.update_table_button, function=self.update_table)
		self.update_number_of_companies_input()

	@BaseController.log_call
	def update_table(self):

		if self.earnings_data_set.empty:
			self.earnings_data_set = self.fetch_earnings_calendar()

		self.earnings_data_view = self.earnings_data_set
		self.earnings_data_view = pandas.merge(
			left=self.earnings_data_view,
			right=self.constituents_data_set[['asset', 'name', 'weight_percentage']],
			left_on='symbol',
			right_on='asset',
			how='right',
		)
		self.earnings_data_view = self.earnings_data_view.sort_values(
			by='weight_percentage', ascending=False
		)
		self.earnings_data_view = self.earnings_data_view.head(self.number_of_companies_input.value)

		self.cds.data = self.earnings_data_view
		self.columns = self.earnings_data_view

		#Update view components
		self.table.columns = self.columns
		self.table.source = self.cds

	@BaseController.log_call
	def update_number_of_companies_input(self):
		#Update view components
		self.constituents_data_set = self.fetch_index_constituents(index=self.index_selector.value)

		max_number_of_companies = len(self.constituents_data_set)

		self.number_of_companies_input.value = max_number_of_companies
