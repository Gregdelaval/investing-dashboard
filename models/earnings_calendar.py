from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
from bokeh import models


class EarningsCalendar(BaseModels, DataProvier):

	def __init__(self) -> None:
		super().__init__()
		#Define help texts
		self.sidebar_title = self.divider(text='Earnings Calendar')
		self.index_description = self.pretext(text='Select index calendar.')
		self.number_of_companies_description = self.pretext(text='Show # of companies')

		# Define widgets controllers
		self.index_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_widgets,
			options=['S&P 500', 'Nasdaq 100'],
		)
		self.number_of_companies_spinner = self.spinner(
			self.set_data_view,
			self.set_source,
			low=1,
			high=100,
			step=1,
			value=15,
		)

		#Invoke all event handlers
		self.set_data_set('', '', '')
		self.set_data_view('', '', '')
		self.set_source('', '', '')

		#Define table
		columns = self.table_columns(
			self.data_view,
			formats={'weight': models.NumberFormatter(format='0.00%')},
		)
		self.table = self.define_table(
			source=self._source,
			columns=columns,
		)

	def set_data_set(self, attrname, old, new) -> None:
		self.data_set = self.fetch_earnings_calendar(index=self.index_selector.value)

	def set_data_view(self, attrname, old, new) -> None:
		self.data_view = self.data_set
		#Only show data for currently toggled index dropdown value
		self.data_view = self.data_view.loc[self.data_view['index'] == self.index_selector.value]
		self.data_view = self.data_view.sort_values(by='weight', ascending=False, ignore_index=True)
		#Only amount of highlighted options
		self.data_view = self.data_view.head(self.number_of_companies_spinner.value)

	def set_widgets(self, attrname, old, new) -> None:
		self.number_of_companies_spinner.update(high=len(self.data_set))

	def set_source(self, attrname, old, new) -> None:
		try:
			_source = self.column_data_source(self.data_view)
			self._source.data.update(_source.data)
		except AttributeError:
			self._source = self.column_data_source(self.data_view)
