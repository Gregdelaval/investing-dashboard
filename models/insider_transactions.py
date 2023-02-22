from .base_models import BaseModels
from ..helpers.data_provider import DataProvier


class InsiderTransactions(BaseModels, DataProvier):

	def __init__(
		self,
		chart_width: int,
		chart_height: int,
	) -> None:
		super().__init__()

		#TODO improve performance

		#Set chart dimensions
		self.chart_width = chart_width
		self.chart_height = chart_height

		#Fetch controllers input
		# transaction_types = self.fetch_transaction_types()['transaction_type'].values.tolist()

		#Set controllers
		# self.transaction_type_selector = self.selector(
		# 	title='Transaction type',
		# 	options=transaction_types,
		# )
		self.group_by_controller = self.selector(
			title='Group by',
			options=['transaction_type', 'acquistion_or_disposition'],
		)
		self.aggregation_controller = self.selector(
			title='Aggregate on',
			options=['price', 'volume'],
			value='volume',
		)
		self.scale_to_index = self.selector(
			title='Scale to index',
			options=[None, 'S&P 500', 'Nasdaq 100'],
			sort=False,
		)

		self.set_data_set()
		self.set_data_view()
		self.set_source()

		#Define glyphs
		self._figure_line = self.define_line(
			x='YW',
			y='securities_transacted',
		)

		#Define figure
		self.figure = self.define_figure(
			width=self.chart_width,
			height=self.chart_height,
		)

		self.figure.add_glyph(self._insider_transactions_source, self._figure_line)

	def set_data_set(self) -> None:
		self.insider_transactions_data_set = self.fetch_insider_transactions(
			scale_to_index=self.scale_to_index.value,
			group_by=self.group_by_controller.value,
			aggregate_on=self.aggregation_controller.value,
		)

	def set_data_view(self) -> None:
		self.insider_transactions_data_view = self.insider_transactions_data_set

	def set_source(self) -> None:
		try:
			self._insider_transactions_source.data.update(
				self.column_data_source(self.insider_transactions_data_view).data
			)
		except AttributeError:
			self._insider_transactions_source = self.column_data_source(self.insider_transactions_data_view)
