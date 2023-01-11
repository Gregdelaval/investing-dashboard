import os
import logging
import sys
import pandas
import typing


class Helpers():

	def __init__(self) -> None:
		pass

	def load_variables(self, root: str) -> None:
		os.environ['PATH_ROOT'] = root
		os.environ['PATH_CACHE'] = root + 'cache//'

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

	def match_closest_neighbor_index(
		self,
		parent_df: pandas.DataFrame,
		child_df: pandas.DataFrame,
		parent_merge_on: str,
		child_merge_on: str,
		appended_neighbor_index_col_name: str = 'position',
	) -> pandas.DataFrame:
		"""Matches closest index of parent df given child df

		Args:
			parent_df (pandas.DataFrame): Parent DF to find closest index of
			child_df (pandas.DataFrame): Child DF to inherit parents index
			parent_merge_on (str): Parents column to use for matching
			child_merge_on (str): Childs column to use for matching
			appended_neighbor_index_col_name (str, optional): What to call the appended column referencing parents closest neighbor. Defaults to 'position'.

		Returns:
			pandas.DataFrame: Child DF with appended_neighbor_index_col_name (arg).
		"""
		#Make a copy of the parent df
		parent_df_copy = parent_df.copy(deep=True)
		#Tag child's columns to keep after merge
		for col in child_df.columns.tolist():
			child_df.rename(columns={col: f'keep_this_col_{col}'}, inplace=True)
		parent_df_copy[f'keep_this_col_{appended_neighbor_index_col_name}'] = parent_df_copy.index

		#merge df's
		child_df = pandas.merge_asof(
			child_df,
			parent_df_copy,
			left_on=f'keep_this_col_{child_merge_on}',
			right_on=parent_merge_on,
			direction='nearest',
		)
		#merge remove untagged columns from child
		col_to_drop = [col for col in child_df.columns.tolist() if 'keep_this_col_' not in col]
		child_df = child_df.drop(columns=col_to_drop)

		#rename childs colums back to original
		for col in child_df.columns.tolist():
			child_df.rename(columns={col: col.replace('keep_this_col_', '')}, inplace=True)

		return child_df


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