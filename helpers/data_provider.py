from .helpers import Helpers
from sqlalchemy import create_engine
import pandas
import os
import hashlib


class DataProvier():
	log = Helpers().get_logger(__name__)
	engine = create_engine(
		url=
		f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
	)

	def __init__(self) -> None:
		pass

	def query(
		self,
		sql_query: str,
		cache: bool = True,
	) -> pandas.DataFrame:
		"""Fetches data from MySql DB or cache based on provided sql query.

		Args:
			sql_query (str): MySql query
			cache (bool): Stores result of provided query for future use.
			If the query does not return a healthy response, it will not be stored to cache.
			Defaults to True.

		Returns:
			pandas.DataFrame:
		"""
		sql_query = sql_query.replace('%', r'%%')

		if cache:
			cached_file_name = os.getenv('PATH_CACHE') + hashlib.sha256(str.encode(sql_query)).hexdigest()
			if Helpers().file_exists(file=cached_file_name):
				self.log.debug(f'Cached response exists, returning it.')
				df = pandas.read_pickle(cached_file_name)
				return df
			self.log.debug(f'Cached response does not exist.')

		self.log.info(f'Fetching data from MySql DB with following query:\n{sql_query}')
		try:
			df = pandas.read_sql_query(sql_query, con=self.engine)
			self.log.debug('Fetched successfully')
		except Exception as e:
			self.log.error(f'Failed executing following query:\n {sql_query}\nDue to:\n{repr(e)}')
			return pandas.DataFrame

		if cache:
			self.log.debug(f'Storing response in cache.')
			df.to_pickle(cached_file_name)

		return df

	def fetch_earnings_calendar(self) -> pandas.DataFrame:
		"""Fetches earnings calendar

		Returns:
			pandas.DataFrame:
		"""

		sql_query = fr'''
		WITH constituents AS
		(
			SELECT  `symbol`,
					`name`,
					`weight`,
					`index`
			FROM `dl_index_information`.`index_constituents`
		), calendar AS
		(
			SELECT  `symbol`,
					`date`,
					`time`
			FROM `dl_earnings`.`calendar`
		)
		SELECT  constituents.`symbol`,
				constituents.`name`,
				constituents.`weight`,
				constituents.`index`,
				calendar.`date`,
				calendar.`time`
		FROM constituents
		LEFT JOIN calendar
		ON constituents.`symbol` = calendar.`symbol`
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
		sql_query = f'SELECT `common_name` FROM `dl_investing_instruments`.`symbols_mapping`'
		df = self.query(sql_query=sql_query)
		return df

	def fetch_investing_instrument(self, symbol: str, granularity: str) -> pandas.DataFrame:
		sql_query = fr'SELECT * FROM `dl_investing_instruments`.`{symbol}_{granularity}`'
		df = self.query(sql_query=sql_query)
		return df

	def fetch_portfolio_historical_positions(self):
		sql_query = fr'''
		WITH historical_positions AS
		(
			SELECT  *
			FROM `dl_portfolio`.`gregdelaval_etoro_portfolio_history`
		) , mapping AS
		(
			SELECT  `instrument_id`,
					`name`,
					`occurred_at`
			FROM `dl_portfolio`.`gregdelaval_etoro_portfolio_activity`
		) , symbols AS
		(
			SELECT  *
			FROM `dl_investing_instruments`.`symbols_mapping`
		)
		SELECT  DISTINCT symbols.`common_name`,
				historical_positions.`open_datetime`,
				historical_positions.`open_rate`,
				historical_positions.`is_buy`,
				historical_positions.`close_datetime`,
				historical_positions.`close_rate`,
				historical_positions.`close_reason`,
				historical_positions.`net_profit`,
				historical_positions.`leverage`,
				mapping.`name`
		FROM historical_positions
		JOIN mapping
		ON historical_positions.`instrument_id` = mapping.`instrument_id`
		JOIN symbols
		ON mapping.`name` = symbols.`etoro_name`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_portfolio_open_positions(self):
		sql_query = fr'''
		WITH open_positions AS
		(
			SELECT  *
			FROM `dl_portfolio`.`gregdelaval_etoro_positions`
		) , mapping AS
		(
			SELECT  `instrument_id`,
					`name`,
					`occurred_at`
			FROM `dl_portfolio`.`gregdelaval_etoro_portfolio_activity`
		) , symbols AS
		(
			SELECT  *
			FROM `dl_investing_instruments`.`symbols_mapping`
		)
		SELECT  DISTINCT symbols.`common_name`,
				open_positions.`open_datetime`,
				open_positions.`open_rate`,
				open_positions.`is_buy`,
				open_positions.`take_profit_rate`,
				open_positions.`stop_loss_rate`,
				open_positions.`amount`,
				open_positions.`leverage`,
				mapping.`name`
		FROM open_positions
		JOIN mapping
		ON open_positions.`instrument_id` = mapping.`instrument_id`
		JOIN symbols
		ON mapping.`name` = symbols.`etoro_name`
		'''
		df = self.query(sql_query=sql_query)
		return df
