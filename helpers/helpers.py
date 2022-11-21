import os
import logging
import sys
import shutil
import pandas
import typing


class Helpers():

	def __init__(self) -> None:
		pass

	def load_variables(self, root: str) -> None:
		os.environ['PATH_ROOT'] = root
		os.environ['PATH_CACHE'] = root + 'cache//'

	def clear_cache(self) -> None:
		shutil.rmtree(os.getenv('PATH_CACHE'), ignore_errors=True)
		os.makedirs(os.getenv('PATH_CACHE'), exist_ok=True)

	def get_logger(self, name: str) -> logging.Logger:
		"""Gets custom logger that does not get handlers propagatedby Bokeh's own logger.

		Args:
			name (str): Name of logger

		Returns:
			logging.Logger:
		"""
		logger = logging.getLogger(name)
		logger.propagate = False
		logger.setLevel(logging.DEBUG)
		stream_handler = logging.StreamHandler(sys.stdout)
		stream_handler.setFormatter(_CustomColoredFormatter())
		logger.addHandler(stream_handler)
		return logger

	def file_exists(self, file: str) -> bool:
		return os.path.isfile(file)

	def find_closest_neighbour(
		self,
		for_value: typing.Union[int, pandas.Timestamp],
		in_df: pandas.DataFrame,
		in_column: str,
	) -> int:
		# def find_closest_neighbour(_dt):
		# 	#Get neighbour datetimes
		# 	lower_dt = self.ohlc_data_view[self.ohlc_data_view['datetime'] < _dt]['datetime']
		# 	higher_dt = self.ohlc_data_view[self.ohlc_data_view['datetime'] > _dt]['datetime']
		# 	try:
		# 		lower_dt_index = lower_dt.idxmax()
		# 	except ValueError:
		# 		lower_dt_index = 0
		# 	try:
		# 		higher_dt_index = higher_dt.idxmin()
		# 	except ValueError:
		# 		higher_dt_index = 0

		# 	#Return neighbour index based on distance
		# 	lower_dt_distance = abs(self.ohlc_data_view.iloc[lower_dt_index]['datetime'] - _dt)
		# 	higher_dt_distance = abs(self.ohlc_data_view.iloc[higher_dt_index]['datetime'] - _dt)
		# 	if lower_dt_distance < higher_dt_distance:
		# 		return lower_dt_index
		# 	return higher_dt_index

		#Get neighbour datetimes
		lower_dt = in_df[in_df[in_column] < for_value][in_column]
		higher_dt = in_df[in_df[in_column] > for_value][in_column]
		try:
			lower_dt_index = lower_dt.idxmax()
		except ValueError:
			lower_dt_index = 0
		try:
			higher_dt_index = higher_dt.idxmin()
		except ValueError:
			higher_dt_index = 0

		#Return neighbour index based on distance
		lower_dt_distance = abs(in_df.iloc[lower_dt_index][in_column] - for_value)
		higher_dt_distance = abs(in_df.iloc[higher_dt_index][in_column] - for_value)
		if lower_dt_distance < higher_dt_distance:
			return lower_dt_index
		return higher_dt_index


class _CustomColoredFormatter(logging.Formatter):
	'''Logging Formatter to add colors and define format per logging level'''
	_format = '%(levelname)s:%(asctime)s | %(filename)s:%(lineno)d:\n%(message)s'
	FORMATS = {
		logging.DEBUG: f'\x1b[38;21m{_format}\x1b[0m',
		logging.INFO: f'\x1b[1;34m{_format}\x1b[0m',
		logging.WARNING: f'\x1b[33;21m{_format}\x1b[0m',
		logging.ERROR: f'\x1b[31;21m{_format}\x1b[0m',
		logging.CRITICAL: f'\x1b[31;1m{_format}\x1b[0m',
	}

	def format(self, record):
		log_format = self.FORMATS[record.levelno]
		formatter = logging.Formatter(log_format)
		formatter.datefmt = '%Y-%m-%dT%H:%M:%S'
		return formatter.format(record)