from .base_models import BaseModels
from ..helpers.data_provider import DataProvier
from bokeh import models


class InvestingChart(BaseModels, DataProvier):

	def __init__(self) -> None:
		super().__init__()