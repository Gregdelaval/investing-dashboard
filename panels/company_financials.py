from .base import BaseView, BaseController, BaseModel
from bokeh import models, plotting, events
from bokeh.layouts import gridplot, column, row
import pandas
from typing import List


class CompanyFinancialsView(BaseView):

	def __init__(
		self,
		logger_name,
		chart_width,
		chart_height,
		panel_title,
	) -> None:
		super().__init__(logger_name)
		#Controllers
		self._financial_statement_selector = models.Select(
			title='Financial Statement',
			options=[
			('balance_sheet_statement', 'Balance Sheet'),
			('cash_flow_statement', 'Cash Flow'),
			('income_statement', 'Income Statement'),
			],
			value='balance_sheet_statement',
		)
		self._periodicity_selector = models.Select(
			title='Periodicity',
			options=[
			('annual', 'Annual'),
			('quarterly', 'Quarterly'),
			],
			value='annual',
		)
		self._company_selector = models.Select(
			title='Company',
			value=None,
		)
		self._financial_kpi_selector = models.Select(
			title='KPI',
			value=None,
		)
		self._calculation_button = models.Button(label='Update')

		#Define Figure
		self._financials_chart = plotting.figure(
			active_scroll='wheel_zoom',
			width=chart_width,
			height=chart_height,
			background_fill_alpha=0.5,
			x_range=[0, 1],
			y_range=[0, 1],
		)
		self.financials_chart.yaxis[0].formatter = models.NumeralTickFormatter(format='0.00 a')
		self.financials_chart.ygrid.grid_line_color = None
		self.financials_chart.yaxis.major_label_text_color = "white"
		self.financials_chart.xaxis.major_label_text_color = "white"

		self._vbar_glyph = models.VBar(
			x='index',
			bottom='bottom',
			top='top',
			width=0.9,
			tags=['vbar'],
			fill_color='#00eeff',
		)

		#Panel
		_widgets_column = self.fit_column_content(
			column_width=300,
			content=column(
			row(
			self.financial_statement_selector,
			self.company_selector,
			),
			row(
			self.periodicity_selector,
			self.financial_kpi_selector,
			),
			self.calculation_button,
			)
		)
		self._layout = gridplot(
			toolbar_location='left',
			merge_tools=True,
			toolbar_options=dict(logo=None),
			children=[[_widgets_column, self.financials_chart]]
		)
		self._panel = models.TabPanel(
			child=self.layout,
			title=panel_title,
		)

	@property
	def vbar_glyph(self):
		return self._vbar_glyph

	@property
	def calculation_button(self):
		return self._calculation_button

	@property
	def layout(self):
		return self._layout

	@property
	def panel(self):
		return self._panel

	@property
	def financials_chart(self):
		return self._financials_chart

	@property
	def financial_statement_selector(self):
		return self._financial_statement_selector

	@property
	def company_selector(self):
		return self._company_selector

	@property
	def periodicity_selector(self):
		return self._periodicity_selector

	@property
	def financial_kpi_selector(self):
		return self._financial_kpi_selector


class CompanyFinancialsModel(BaseModel):

	def __init__(self, logger_name) -> None:
		super().__init__(logger_name)

		self._financial_data_set = pandas.DataFrame()
		self._financial_data_view = pandas.DataFrame()
		self._financial_cds = plotting.ColumnDataSource(self._financial_data_view)

		self._available_symbols = List[str]
		self._available_kpis = List[str]

	@property
	def financial_cds(self) -> plotting.ColumnDataSource:
		return self._financial_cds

	@property
	def financial_data_set(self) -> pandas.DataFrame:
		return self._financial_data_set

	@financial_data_set.setter
	def financial_data_set(self, df: pandas.DataFrame) -> None:
		self._financial_data_set = df

	@property
	def financial_data_view(self) -> pandas.DataFrame:
		return self._financial_data_view

	@financial_data_view.setter
	def financial_data_view(self, df: pandas.DataFrame) -> None:
		self._financial_data_view = df

	@property
	def available_symbols(self) -> List[str]:
		return self._available_symbols

	@available_symbols.setter
	def available_symbols(self, df: pandas.DataFrame) -> None:
		self._available_symbols = sorted(df['symbol'].values.tolist())

	@property
	def available_kpis(self) -> List[str]:
		return self._available_kpis

	@available_kpis.setter
	def available_kpis(self, df: pandas.DataFrame) -> None:
		self._available_kpis = df.columns.tolist()


class CompanyFinancials(CompanyFinancialsView, CompanyFinancialsModel, BaseController):

	def __init__(self,) -> None:
		super().__init__(
			logger_name=__name__,
			chart_width=16 * 80,
			chart_height=9 * 80,
			panel_title='Company Financials',
		)

		self.available_symbols = self.fetch_available_symbols_company_financials()
		self.company_selector.options = self.available_symbols
		self.company_selector.value = self.company_selector.options[0]
		self.append_callback(model=self.financial_statement_selector, function=self.update_available_kpis)
		self.append_callback(model=self.calculation_button, function=self.update_figure)
		self.append_callback(model=self.calculation_button, function=self.update_view_range, set_full=True) #Yapf:disable
		self.append_callback(model=self.financials_chart, function=self.update_view_range, event_type=events.MouseWheel)  # yapf: disable

		self.update_available_kpis()

	@BaseController.log_call
	def update_available_kpis(self):
		#Update model
		self.available_kpis = self.fetch_available_kpis_company_financials(
			table=f'{self.periodicity_selector.value}_{self.financial_statement_selector.value}'
		)
		[
			self.available_kpis.remove(_i) for _i in [
			'accepted_date',
			'calendar_year',
			'cik',
			'date',
			'filling_date',
			'final_link',
			'id',
			'link',
			'period',
			'reported_currency',
			'symbol',
			]
		]

		#Update view
		self.financial_kpi_selector.options = self.available_kpis
		self.financial_kpi_selector.value = self.financial_kpi_selector.options[0]

	@BaseController.log_call
	def update_figure(self):
		#Update model
		self.financial_data_set = self.fetch_financial_kpi(
			kpis=[self.financial_kpi_selector.value],
			periodcity=self.periodicity_selector.value,
			statement=self.financial_statement_selector.value,
		)

		self.financial_data_view = self.financial_data_set
		self.financial_data_view = self.filter_data_frame(
			self.financial_data_view,
			column='symbol',
			value=self.company_selector.value,
		)
		self.financial_data_view = self.financial_data_view.rename(
			columns={self.financial_kpi_selector.value: 'top'}
		)
		self.financial_data_view['bottom'] = 0
		self.financial_data_view = self.financial_data_view.sort_values(by=['calendar_year', 'period'])
		self.financial_data_view = self.financial_data_view.reset_index()
		self.financial_data_view['index'] = self.financial_data_view.index
		self.financial_cds.data.update(self.financial_data_view)

		self.financial_data_view['x_axis_label'] = \
   self.financial_data_view['period'] + \
   ' ' + \
   self.financial_data_view['calendar_year'].astype(str)

		#Update view
		if len(self.financials_chart.select({'id': self.vbar_glyph.id})) == 0:
			self.financials_chart.add_glyph(self.financial_cds, self.vbar_glyph)

		self.financials_chart.xaxis.major_label_overrides = self.financial_data_view[
			'x_axis_label'].astype(str).to_dict()

	def update_view_range(self, set_full=False):
		_df = self.financial_data_view

		#X-axis
		if set_full:
			self.financials_chart.x_range.end = _x_range_max = _df.index.max() + 1
			self.financials_chart.x_range.start = _x_range_min = -1
		else:
			_x_range_min = self.financials_chart.x_range.start
			_x_range_max = self.financials_chart.x_range.end

		#Y-axis
		_mask = (_df.index >= _x_range_min) & (_df.index <= _x_range_max)
		_max_value = _df.loc[_mask]['top'].max()
		if _df.loc[_mask]['top'].min() < 0:
			_min_value = _df.loc[_mask]['top'].min()
		else:
			_min_value = 0
		self.financials_chart.y_range.start = _min_value
		self.financials_chart.y_range.end = _max_value
