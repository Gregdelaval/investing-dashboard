from .helpers import Helpers
from sqlalchemy import create_engine
import pandas
import os


class DataProvier():
	log = Helpers().get_logger(__name__)
	engine = create_engine(
		url=
		f"mysql+pymysql://{os.getenv('mysql_user')}:{os.getenv('mysql_password')}@{os.getenv('mysql_host')}:{os.getenv('mysql_port')}"
	)

	def __init__(self) -> None:
		pass

	def query(
		self,
		sql_query: str,
	) -> pandas.DataFrame:
		"""Fetches data from MySql DB based on provided sql query

		Args:
			sql_query (str): MySql query

		Returns:
			pandas.DataFrame:
		"""
		sql_query = sql_query.replace('%', r'%%')
		self.log.info(f'Fetching data from MySql DB with following query:\n{sql_query}')
		try:
			df = pandas.read_sql_query(sql_query, con=self.engine)
			self.log.debug('Fetched successfully')
			return df
		except Exception as e:
			self.log.error(f'Failed executing following query:\n {sql_query}\nDue to:\n{repr(e)}')
			return pandas.DataFrame

	def fetch_earnings_calendar(self, index: str) -> pandas.DataFrame:
		"""Fetches earnings for passed index

		Args:
			index (str): Index to fetch earnings calendar for.

		Returns:
			pandas.DataFrame:
		"""

		sql_query = fr'''
		WITH constituents as (
			SELECT `symbol`, `name`, `weight`, `index`
			FROM `dl_index_information`.`index_constituents`
			WHERE `index` = '{index}'
			ORDER BY `weight` DESC
		),
		calendar as (
			SELECT `symbol`, `date`, `time`
			FROM `dl_earnings`.`calendar`
			)
		SELECT constituents.`symbol`, constituents.`name`, constituents.`weight`, constituents.`index`, calendar.`date`, calendar.`time`
		FROM constituents
		LEFT JOIN calendar ON constituents.`symbol` = calendar.`symbol`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_financial_statement(self, financial_statement: str) -> pandas.DataFrame:
		"""Fetches table containing passed financials statement for all companies

		Args:
			financial_statement (str): 'Balance Sheet'|'Cash Flow'|'Income Statements'

		Returns:
			pandas.DataFrame:
		"""
		financial_statements = {
			'Balance Sheet': 'balance_sheet_statements',
			'Cash Flow': 'cash_flow_statements',
			'Income Statements': 'income_statements',
		}
		sql_query = fr'SELECT * FROM `dl_earnings`.`{financial_statements[financial_statement]}`'
		df = self.query(sql_query=sql_query)
		return df

	def fetch_symbols_mapping(self) -> pandas.DataFrame:
		sql_query = f'SELECT * FROM `dl_investing_instruments`.`symbols_mapping`'
		df = self.query(sql_query=sql_query)
		return df

	def fetch_investing_instrument(self, symbol: str, granularity: str) -> pandas.DataFrame:
		sql_query = fr'SELECT * FROM `dl_investing_instruments`.`{symbol}_{granularity}`'
		df = self.query(sql_query=sql_query)
		return df