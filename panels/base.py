from bokeh import models, events, layouts
from typing import List, Callable, Literal
from sqlalchemy import create_engine
from functools import wraps
import pandas
import os
import hashlib
import time
from ..helpers.helpers import Helpers


class Base:

	def __init__(
		self,
		logger_name: str,
	) -> None:
		self.log = Helpers().get_logger(logger_name)

	def log_call(func: Callable):
		"""
		Decorator for wrapping function with logging of called function name, arguments and execution time.
		"""

		@wraps(func)
		def wrapper(self, *args, **kwargs):
			self.log.info(f'Calling function: {func.__name__}. Args:\n{list(args)} {dict(kwargs)}')
			_start = time.time()
			_r = func(self, *args, **kwargs)
			self.log.info(f'Function {func.__name__} finished. Execution time: {round(time.time()-_start, 2)}') #Yapf: disable
			return _r

		return wrapper


class BaseModel(Base):
	engine = create_engine(
		url=
		f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
	)

	def __init__(self, logger_name) -> None:
		super().__init__(logger_name=logger_name)

	def inherit_closest_index(
		self,
		parent_df: pandas.DataFrame,
		child_df: pandas.DataFrame,
		parent_on: str,
		child_on: str,
	) -> pandas.DataFrame:
		child_df = child_df.sort_values(by=child_on)
		child_df = pandas.merge_asof(
			child_df,
			parent_df[[parent_on, 'index']],
			left_on=child_on,
			right_on=parent_on,
			direction='nearest'
		)
		child_df.drop(columns=[parent_on], inplace=True)
		return child_df

	@Base.log_call
	def filter_data_frame(self, df: pandas.DataFrame, column: str, value: str) -> pandas.DataFrame:
		return df.loc[df[column] == value]

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
			return pandas.DataFrame()

		if cache:
			try:
				self.log.debug(f'Storing response in cache.')
				df.to_pickle(cached_file_name)
			except Exception as e:
				self.log.error(f'Failed writing cache with cached_file_name: {cached_file_name}')

		return df

	def fetch_financial_kpi(
		self,
		kpis: List[str],
		periodcity: Literal['annual', 'quarterly'],
		statement: Literal['balance_sheet_statement', 'cash_flow_statement', 'income_statement'],
	) -> pandas.DataFrame:
		sql_query = fr'''
		SELECT calendar_year, period, symbol, {', '.join(kpis)}
		FROM dl_company_information.{periodcity}_{statement}
		'''
		return self.query(sql_query=sql_query)

	def fetch_available_symbols_company_financials(self) -> pandas.DataFrame:
		sql_query = '''
		SELECT DISTINCT(symbol)
		FROM dl_company_information.annual_balance_sheet_statement
		'''
		return self.query(sql_query=sql_query)

	def fetch_available_kpis_company_financials(self, table) -> pandas.DataFrame:
		sql_query = f'''
		SELECT *
		FROM dl_company_information.{table}
		LIMIT 1
		'''
		return self.query(sql_query=sql_query)

	def fetch_portfolio_overview(self) -> pandas.DataFrame:
		sql_query = '''
		WITH portfolio_overview AS
		(
			SELECT `direction`, `instrument_id`, `invested`, `net_profit`, `value`
			FROM `dl_portfolio`.`etoro_aggregated_positions`
		) , etoro_mapping AS
		(
			SELECT `instrument_id`, `symbol_full`
			FROM `dl_portfolio`.`etoro_symbols_mapping`
		), symbols_mapping AS
		(
			SELECT `common_name`, `etoro_name`
			FROM `dl_supplied_tables`.`symbols_mapping`
		)
		SELECT	etoro_mapping.`symbol_full` as etoro_symbol_name,
				symbols_mapping.`common_name`,
				portfolio_overview.`direction`,
				portfolio_overview.`invested`,
				portfolio_overview.`net_profit`,
				portfolio_overview.`value`
		FROM portfolio_overview
		JOIN etoro_mapping
			ON portfolio_overview.`instrument_id` = etoro_mapping.`instrument_id`
		LEFT JOIN symbols_mapping
			ON etoro_mapping.`symbol_full` = symbols_mapping.`etoro_name`
		'''
		return self.query(sql_query=sql_query)

	def fetch_earnings_calendar(self) -> pandas.DataFrame:
		sql_query = fr'''
		SELECT `date`, `fiscal_date_ending`,`symbol`,  `time`
		FROM dl_company_information.earnings_calendar
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_available_index_constituents(self) -> pandas.DataFrame:
		sql_query = fr'''
		SELECT common_name
		FROM dl_supplied_tables.symbols_mapping
		WHERE tradeable_etf <> ""
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_index_constituents(self) -> pandas.DataFrame:
		sql_query = fr'''
		SELECT `asset`, `name`, `weight_percentage`, `common_index_name`
		FROM dl_index_information.consolidated_constituents_weights
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_instrument_data(self, instrument, granularity):
		sql_query = f'''
		SELECT `datetime`, `open`, `high`, `low`, `close`
		FROM `dl_investing_instruments`.`{instrument}_{granularity}`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_portfolio_open_orders(self):
		sql_query = r'''
		WITH open_orders AS
		(
			SELECT  `amount`,
					`execution_type`,
					`instrument_id`,
					`leverage`,
					`order_id`,
					`is_buy`,
					`open_date_time`,
					`rate`,
					`stop_loss_rate`,
					`take_profit_rate`
			FROM `dl_portfolio`.`etoro_open_orders`
		) , mapping AS
		(
			SELECT  `instrument_id`,
					`symbol_full`
			FROM `dl_portfolio`.`etoro_symbols_mapping`
		)
		SELECT  mapping.`symbol_full`,
				open_orders.`amount`,
				open_orders.`execution_type`,
				open_orders.`instrument_id`,
				open_orders.`leverage`,
				open_orders.`order_id`,
				open_orders.`is_buy`,
				open_orders.`open_date_time`,
				open_orders.`rate`,
				open_orders.`stop_loss_rate`,
				open_orders.`take_profit_rate`
		FROM open_orders
		JOIN mapping
		ON open_orders.`instrument_id` = mapping.`instrument_id`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_portfolio_closed_positions(self):
		sql_query = r'''
		WITH historical_positions AS
		(
			SELECT  `instrument_id`,
					`close_date_time`,
					`close_rate`,
					`close_reason`,
					`is_buy`,
					`leverage`,
					`net_profit`,
					`open_date_time`,
					`open_rate`,
					`position_id`
			FROM `dl_portfolio`.`etoro_portfolio_history`
		) , mapping AS
		(
			SELECT  `instrument_id`,
					`symbol_full`
			FROM `dl_portfolio`.`etoro_symbols_mapping`
		)
		SELECT  mapping.`symbol_full`,
				historical_positions.`instrument_id`,
				historical_positions.`close_date_time`,
				historical_positions.`close_rate`,
				historical_positions.`close_reason`,
				historical_positions.`is_buy`,
				historical_positions.`leverage`,
				historical_positions.`net_profit`,
				historical_positions.`open_date_time`,
				historical_positions.`open_rate`,
				historical_positions.`position_id`
		FROM historical_positions
		JOIN mapping
		ON historical_positions.`instrument_id` = mapping.`instrument_id`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_portfolio_open_positions(self):
		sql_query = r'''
		WITH open_positions AS
		(
			SELECT `instrument_id`, `is_buy`, `open_date_time`, `stop_loss_rate`, `take_profit_rate`, `open_rate`
			FROM `dl_portfolio`.`etoro_positions`
		) , mapping AS
		(
			SELECT `instrument_id`, `symbol_full`
			FROM `dl_portfolio`.`etoro_symbols_mapping`
		)
		SELECT	mapping.`symbol_full`,
				open_positions.`open_date_time`,
				open_positions.`is_buy`,
				open_positions.`open_rate`,
				open_positions.`take_profit_rate`,
				open_positions.`stop_loss_rate`
		FROM open_positions
		JOIN mapping
		ON open_positions.`instrument_id` = mapping.`instrument_id`
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_instrument_exposure_data(self):
		sql_query = r'''
		WITH labeled_positions AS (
			SELECT mapping.`symbol_full` as etoro_name,
				symbols.`common_name`,
				etoro_positions.`amount`,
				etoro_positions.`leverage`,
				etoro_positions.`is_buy`
			FROM `dl_portfolio`.`etoro_positions` AS etoro_positions
			JOIN `dl_portfolio`.`etoro_symbols_mapping` AS mapping
			ON etoro_positions.`instrument_id` = mapping.`instrument_id`
			JOIN `dl_supplied_tables`.`symbols_mapping` AS symbols
			ON mapping.`symbol_full` = symbols.`etoro_name`
			UNION ALL
			SELECT parent_username as etoro_name,
				parent_username as common_name,
				invested as amount,
				1 as leverage,
				1 as is_buy
			FROM `dl_portfolio`.`etoro_aggregated_mirrors`
		), aggregated_exposure AS (
			SELECT etoro_name, common_name,
				SUM(CASE
					WHEN is_buy = 0 THEN -amount * leverage
					ELSE amount * leverage
				END) AS real_exposure
			FROM labeled_positions
			GROUP BY etoro_name, common_name
		), available_credit AS (
			SELECT realized_credit
			FROM `dl_portfolio`.`etoro_credit`
		), scaled_aggregated_exposure AS (
			SELECT ae.etoro_name as instrument,
			ae.real_exposure as instrument_exposure,
			ae.real_exposure * (1-(ac.realized_credit / 100)) as scaled_instrument_exposure
			FROM aggregated_exposure ae, available_credit ac
		)
		SELECT *
		FROM scaled_aggregated_exposure
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_sector_exposure_data(self):
		sql_query = r'''
		WITH labeled_positions AS (
			SELECT mapping.`symbol_full` as etoro_name,
				symbols.`common_name`,
				mapping.`instrument_type_id`,
				etoro_positions.`amount`,
				etoro_positions.`leverage`,
				etoro_positions.`is_buy`
			FROM `dl_portfolio`.`etoro_positions` AS etoro_positions
			JOIN `dl_portfolio`.`etoro_symbols_mapping` AS mapping
			ON etoro_positions.`instrument_id` = mapping.`instrument_id`
			JOIN `dl_supplied_tables`.`symbols_mapping` AS symbols
			ON mapping.`symbol_full` = symbols.`etoro_name`
			UNION ALL
			SELECT parent_username as etoro_name,
				parent_username as common_name,
				99 as instrument_type_id,
				invested as amount,
				1 as leverage,
				1 as is_buy
			FROM `dl_portfolio`.`etoro_aggregated_mirrors`
		), aggregated_exposure AS (
			SELECT etoro_name, common_name, instrument_type_id,
				SUM(CASE
					WHEN is_buy = 0 THEN -amount * leverage
					ELSE amount * leverage
				END) AS real_exposure
			FROM labeled_positions
			GROUP BY etoro_name, common_name, instrument_type_id
		), aggregated_sector_exposure AS (
			SELECT
				COALESCE(sector_weights.sector, "Unknown") as sector,
				SUM(COALESCE(sector_weights.weight_percentage / 100, 1) * aggregated_exposure.real_exposure) as sector_exposure
			FROM aggregated_exposure
			LEFT JOIN `dl_index_information`.`consolidated_sector_weights` AS sector_weights
			ON aggregated_exposure.`common_name` = sector_weights.`common_index_name`
			GROUP BY sector
		), available_credit AS (
			SELECT realized_credit
			FROM `dl_portfolio`.`etoro_credit`
		), scaled_aggregated_sector_exposure AS (
			SELECT ase.sector,
				ase.sector_exposure,
				ase.sector_exposure * (1-(ac.realized_credit / 100)) as scaled_sector_exposure
			FROM aggregated_sector_exposure ase, available_credit ac
		)
		select * from scaled_aggregated_sector_exposure
		'''
		df = self.query(sql_query=sql_query)
		return df

	def fetch_country_exposure_data(self):
		sql_query = r'''
		WITH labeled_positions AS (
		SELECT mapping.`symbol_full` as etoro_name,
			symbols.`common_name`,
			mapping.`instrument_type_id`,
			etoro_positions.`amount`,
			etoro_positions.`leverage`,
			etoro_positions.`is_buy`
		FROM `dl_portfolio`.`etoro_positions` AS etoro_positions
		JOIN `dl_portfolio`.`etoro_symbols_mapping` AS mapping
		ON etoro_positions.`instrument_id` = mapping.`instrument_id`
		JOIN `dl_supplied_tables`.`symbols_mapping` AS symbols
		ON mapping.`symbol_full` = symbols.`etoro_name`
		UNION ALL
		SELECT parent_username as etoro_name,
			parent_username as common_name,
			99 as instrument_type_id,
			invested as amount,
			1 as leverage,
			1 as is_buy
		FROM `dl_portfolio`.`etoro_aggregated_mirrors`
		), aggregated_exposure AS (
		SELECT etoro_name, common_name, instrument_type_id,
			SUM(CASE
				WHEN is_buy = 0 THEN -amount * leverage
				ELSE amount * leverage
			END) AS real_exposure
		FROM labeled_positions
		GROUP BY etoro_name, common_name, instrument_type_id
		), aggregated_country_exposure AS (
		SELECT
			COALESCE(country_weights.country, "Unknown") as country,
			SUM(COALESCE(country_weights.weight_percentage / 100, 1) * aggregated_exposure.real_exposure) as country_exposure
		FROM aggregated_exposure
			LEFT JOIN `dl_index_information`.`consolidated_country_weights` AS country_weights
			ON aggregated_exposure.`common_name` = country_weights.`common_index_name`
		GROUP BY country
		), available_credit AS (
			SELECT realized_credit
			FROM `dl_portfolio`.`etoro_credit`
		), scaled_aggregated_country_exposure AS (
			SELECT ace.country,
				ace.country_exposure,
				ace.country_exposure * (1-(ac.realized_credit / 100)) as scaled_country_exposure
			FROM aggregated_country_exposure ace, available_credit ac
		)
		select * from scaled_aggregated_country_exposure
		'''
		df = self.query(sql_query=sql_query)
		return df


class BaseController(Base):

	def __init__(self, logger_name) -> None:
		super().__init__(logger_name=logger_name)

	@staticmethod
	def on_change_decorator(func, *args, **kwargs):

		def wrapped_decorator(attr, old, new):

			@wraps(func)
			def wrapper(*args, **kwargs):
				func(*args, **kwargs)

			return wrapper(*args, **kwargs)

		return wrapped_decorator

	@staticmethod
	def on_event_decorator(func, *args, **kwargs):

		def wrapped_decorator(event):

			@wraps(func)
			def wrapper(*args, **kwargs):
				func(*args, **kwargs)

			return wrapper(*args, **kwargs)

		return wrapped_decorator

	@staticmethod
	def toggle_renderers_based_on_tag(
		model: models.Widget,
		tags: List[str],
		visible: bool,
	) -> None:
		glyphs = [glyph.id for glyph in model.select(tags=tags)]

		for renderer in model.renderers:
			for reference in renderer.references():
				if reference.id in glyphs:
					renderer.visible = visible

	def append_callback(
		self,
		model: models.Widget,
		function: Callable,
		trigger=None,
		event_type=None,
		*args,
		**kwargs,
	) -> None:
		"""
		Append on event or on change handler to passed model,
		pass function to be executed by handler and *args, **kwargs
		to be passed to function.

		Args:
			model (models.Widget): Widget to append handler to
			function (Callable): Function handler calls when triggered

		Optional:
		 *args, **kwargs to be passed to function for execution.

		"""
		if model.__class__ == models.Select:
			trigger = 'value'
		if model.__class__ == models.Toggle:
			trigger = 'active'
		if model.__class__ == models.Button:
			event_type = events.ButtonClick

		if event_type is None:
			assert trigger is not None, f'Could not deduct trigger for passed model:\n{model}'
			function = self.on_change_decorator(function, *args, **kwargs)
			model.on_change(trigger, function)
		else:
			function = self.on_event_decorator(function, *args, **kwargs)
			model.on_event(event_type, function)


class BaseView(Base):

	def __init__(self, logger_name) -> None:
		super().__init__(logger_name=logger_name)

	@staticmethod
	def fit_column_content(content: layouts.column, column_width: int = 300) -> layouts.column:
		for _row in content.children:
			if isinstance(_row, models.Row):
				_row_children_width = column_width / len(_row.children) - len(_row.children) * 2
				for _row_child in _row.children:
					if _row_child.width == None:
						_row_child.width = int(_row_children_width)
			else:
				_row.width = column_width

		return content
