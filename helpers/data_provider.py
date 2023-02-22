from .helpers import Helpers
from sqlalchemy import create_engine
import pandas
import os
import hashlib
import functools
import timeit
from typing import Union, Literal

#1. Index search fields CREATE INDEX idx ON dl_company_information.new_index_insider_transactions (`transaction_date`, `securities_transacted`, `symbol`, `price`, `transaction_type`)
#2. Index and use same col types for joins
#3. Select fewest possible cols


class DataProvier():
	log = Helpers().get_logger(__name__)
	engine = create_engine(
		url=
		f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
	)

	def __init__(self) -> None:
		pass

	def timeit_wrapper_decorator(func):

		def wrapper(self, *args, **kwargs):
			starttime = timeit.default_timer()
			_ = func(self, *args, **kwargs)
			self.log.debug(f'Execution time: {str(timeit.default_timer() - starttime)}')
			return _

		return wrapper

	@timeit_wrapper_decorator
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

	def fetch_portfolio_historical_positions(self):
		sql_query = fr'''
		WITH historical_positions as
		(
		SELECT
			*
		FROM
			`dl_portfolio`.`gregdelaval_etoro_portfolio_history`
		)
		,
		mapping as
		(
		SELECT
			`instrument_id`,
			`name`,
			`occurred_at`
		FROM
			`dl_portfolio`.`gregdelaval_etoro_portfolio_activity`
		)
		,
		symbols as
		(
		SELECT
			*
		from
			`dl_investing_instruments`.`symbols_mapping`
		)
		SELECT DISTINCT
		symbols.`common_name`,
		historical_positions.`open_datetime`,
		historical_positions.`open_rate`,
		historical_positions.`is_buy`,
		historical_positions.`close_datetime`,
		historical_positions.`close_rate`,
        historical_positions.`close_reason`,
		historical_positions.`net_profit`,
		historical_positions.`leverage`,
		mapping.`name`
		FROM
		historical_positions
		JOIN
			mapping
			on historical_positions.`instrument_id` = mapping.`instrument_id`
		JOIN
			symbols
			on mapping.`name` = symbols.`etoro_name`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_portfolio_open_positions(self):
		sql_query = fr'''
		WITH open_positions as
		(
		SELECT
			*
		FROM
			`dl_portfolio`.`gregdelaval_etoro_positions`
		)
		,
		mapping as
		(
		SELECT
			`instrument_id`,
			`name`,
			`occurred_at`
		FROM
			`dl_portfolio`.`gregdelaval_etoro_portfolio_activity`
		)
		,
		symbols as
		(
		SELECT
			*
		from
			`dl_investing_instruments`.`symbols_mapping`
		)
		SELECT DISTINCT
		symbols.`common_name`,
		open_positions.`open_datetime`,
		open_positions.`open_rate`,
		open_positions.`is_buy`,
		open_positions.`take_profit_rate`,
		open_positions.`stop_loss_rate`,
		open_positions.`amount`,
		open_positions.`leverage`,
		mapping.`name`
		FROM
		open_positions
		JOIN
			mapping
			on open_positions.`instrument_id` = mapping.`instrument_id`
		JOIN
			symbols
			on mapping.`name` = symbols.`etoro_name`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_insider_transactions(
		self,
		group_by: Union[Literal['transaction_type'], Literal['acquistion_or_disposition']],
		aggregate_on: Union[Literal['price'], Literal['volume']],
		scale_to_index: Union[Literal['S&P 500'], Literal['Nasdaq 100']] = False,
	) -> pandas.DataFrame:

		price = ''
		if aggregate_on == 'price':
			price = ', `price`'

		sql_query = f'''
		SELECT `transaction_date`, `securities_transacted`, `symbol` as `it_symbol`, `{group_by}`{price}
		FROM `dl_company_information`.`new_index_insider_transactions`
		'''
		if scale_to_index:
			sql_query = f'''
			WITH it as (
				{sql_query}
			),
			weights as (
				SELECT `symbol` as `weights_symbol`, `weight`, `index`
				FROM dl_index_information.new_index_constituents
				WHERE `index` = '{scale_to_index}'
			)
			SELECT `transaction_date`, `securities_transacted`, `it_symbol`, `{group_by}`, `weight`, `index`, `weights_symbol`{price}
			FROM it
			JOIN weights on `weights_symbol` = `it_symbol`
			'''

		df = self.query(sql_query=sql_query, cache=False)
		return df


#TODO fix dupes in data:
# SELECT * FROM dl_company_information.insider_transactions
# where `filing_date` = '2022-12-16 18:04:45'
# and `symbol` = 'MSFT'
# and `securities_owned` = '66615.6016'

	def fetch_transaction_types(self):
		sql_query = '''
		SELECT distinct(transaction_type)
		FROM `dl_company_information`.`insider_transactions`
		'''
		df = self.query(sql_query=sql_query)
		return df
