from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
from bokeh import models


class EarningsCalendar(BaseModels, DataProvier):

	def __init__(
		self,
		indices: list,
		table_width: int,
		table_height: int,
	) -> None:
		super().__init__()
		#Define help texts
		self.sidebar_title = self.divider(text='Earnings Calendar')

		# Define widgets controllers
		self.index_selector = self.selector(
			self.set_data_set,
			self.set_data_view,
			self.set_source,
			self.set_widgets,
			title='Select index calendar',
			options=indices,
		)
		self.number_of_companies_spinner = self.spinner(
			self.set_data_view,
			self.set_source,
			title='Show # of companies',
			low=1,
			high=100,
			step=1,
			value=25,
		)

		#Invoke all event handlers
		self.set_data_set()
		self.set_data_view()
		self.set_source()

		#Define table
		columns = self.table_columns(
			self.data_view,
			formats={'weight': models.NumberFormatter(format='0.00%')},
		)
		self.table = self.define_table(
			source=self._source,
			columns=columns,
			width=table_width,
			height=table_height,
		)

	def set_data_set(self) -> None:
		self.data_set = self.fetch_earnings_calendar(index=self.index_selector.value)

	def set_data_view(self) -> None:
		self.data_view = self.data_set
		#Only show data for currently toggled index dropdown value
		self.data_view = self.data_view.loc[self.data_view['index'] == self.index_selector.value]
		self.data_view = self.data_view.sort_values(by='weight', ascending=False, ignore_index=True)
		#Only amount of highlighted options
		self.data_view = self.data_view.head(self.number_of_companies_spinner.value)

	def set_widgets(self) -> None:
		self.number_of_companies_spinner.update(high=len(self.data_set))

	def set_source(self) -> None:
		try:
			_source = self.column_data_source(self.data_view)
			self._source.data.update(_source.data)
		except AttributeError:
			self._source = self.column_data_source(self.data_view)
