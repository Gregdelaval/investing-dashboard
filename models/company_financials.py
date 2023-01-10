from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
import pandas
from typing import List, Tuple


class CompanyFinancials(BaseModels, DataProvier):

	def __init__(self) -> None:
		super().__init__()
		#Define help texts
		self.financials_chart_title = self.divider(text='Company Financials')
		# self.company_selector_description = self.pretext(text='Select company.')
		# self.financial_type_description = self.pretext(text='Select type of financials.')
		# self.financial_kpi_description = self.pretext(text='Select KPI.')
		# self.financial_granularity_description = self.pretext(text='Select fiscal granularity.')
		# self.date_range_description = self.pretext(text='Select period.')

		#Define widgets controllers
		self.financial_type = self.selector(
			self.set_data_set,
			self.set_widgets,
			self.set_data_view,
			self.set_source,
			title='Select type of financials',
			options=['Balance Sheet', 'Cash Flow', 'Income Statements'],
		)
		self.set_data_set('', '', '')

		available_companies = self.define_available_companies(df=self.data_set)
		self.company_selector = self.selector(
			self.set_widgets,
			self.set_data_view,
			self.set_source,
			title='Select company',
			options=available_companies,
		)

		self.financial_granularity = self.selector(
			self.set_data_view,
			self.set_source,
			self.set_widgets,
			title='Select fiscal granularity',
			options=['Annual', 'Quarterly'],
		)

		financial_kpis = self.define_financial_kpis(df=self.data_set)
		self.financial_kpi = self.selector(
			self.set_widgets,
			self.set_data_view,
			self.set_source,
			title='Select KPI',
			options=financial_kpis,
		)

		date_range = self.define_date_range(df=self.data_set)
		self.date_range = self.range_slider(
			self.set_data_view,
			self.set_source,
			self.set_widgets,
			title='Select period',
			start=date_range[0],
			end=date_range[1],
			step=1,
			value=(date_range[0], date_range[1]),
		)
		self.set_data_view('', '', '')
		self.set_source('', '', '')

		#Define chart
		hover_tool = self.define_hover_tool(
			tooltips=[('Period', '@fiscal_period'), ('Value', '@top{,0.00}')]
		)
		self.financials_chart = self.define_bar_chart(
			x='fiscal_period',
			source=self._source,
			hover_tool=hover_tool,
		)

	def set_data_set(self, attrname, old, new) -> None:
		self.data_set = self.fetch_financial_statement(financial_statement=self.financial_type.value)

	def set_data_view(self, attrname, old, new) -> None:
		self.data_view = self.data_set
		#Filter on symbol
		self.data_view = self.data_view.loc[self.data_view['symbol'] == self.company_selector.value]
		#Filter on granularity
		if self.financial_granularity.value == 'Annual':
			self.data_view = self.data_view.loc[self.data_view['period'] == 'FY']
			self.data_view['fiscal_period'] = self.data_view['calendar_year'].astype(str)
		elif self.financial_granularity.value == 'Quarterly':
			self.data_view = self.data_view.loc[self.data_view['period'] != 'FY']
			self.data_view['fiscal_period'] = self.data_view['calendar_year'].astype(str) + self.data_view[
				'period'].astype(str)
		#Sort on date asc
		self.data_view = self.data_view.sort_values(by='date', ascending=True)
		#Filter on KPI
		self.data_view = self.data_view[[self.financial_kpi.value, 'fiscal_period']]
		#Filter on date range
		self.data_view = self.data_view.iloc[int(self.date_range.value[0]):int(self.date_range.value[1])]
		#Rename column
		self.data_view.rename(columns={self.financial_kpi.value: 'top'}, inplace=True)

	def set_widgets(self, attrname, old, new) -> None:
		available_companies = self.define_available_companies(df=self.data_set)
		self.company_selector.update(options=available_companies)
		available_kpi = self.define_financial_kpis(df=self.data_set)
		self.financial_kpi.update(options=available_kpi)
		if self.financial_kpi.value not in available_kpi:
			self.financial_kpi.update(value=available_kpi[0])
		date_range = self.define_date_range(self.data_set)
		self.date_range.update(start=date_range[0], end=date_range[1])
		#Update chart
		self.financials_chart.x_range.factors = self._source.data['fiscal_period']

	def set_source(self, attrname, old, new) -> None:
		try:
			self._source.data = self.data_view.to_dict(orient='list')
		except AttributeError:
			self._source = self.column_data_source(self.data_view)

	def define_date_range(self, df: pandas.DataFrame) -> Tuple[int, int]:
		#Filter on symbol
		df = df.loc[df['symbol'] == self.company_selector.value]
		#Filter on granularity
		if self.financial_granularity.value == 'Annual':
			df = df.loc[df['period'] == 'FY']
			df['fiscal_period'] = df['calendar_year'].astype(str)
		elif self.financial_granularity.value == 'Quarterly':
			df = df.loc[df['period'] != 'FY']
			df['fiscal_period'] = df['calendar_year'].astype(str) + df['period'].astype(str)
		return (0, len(df))

	def define_financial_kpis(self, df: pandas.DataFrame) -> list:
		_columns = df.columns.to_list()
		_columns = sorted(_columns)
		_columns_to_remove = [
			'cik',
			'calendar_year',
			'accepted_date',
			'date',
			'final_link',
			'filling_date',
			'link',
			'period',
			'symbol',
			'extraction_time',
			'reported_currency',
		]
		_columns = [_column for _column in _columns if _column not in _columns_to_remove]
		return _columns

	def define_available_companies(self, df: pandas.DataFrame) -> List[str]:
		unique_symbols = df.symbol.unique().tolist()
		unique_symbols = sorted(unique_symbols)
		return unique_symbols
