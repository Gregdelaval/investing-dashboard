from bokeh.layouts import gridplot, column, row
from bokeh import models
from ..models.company_financials import CompanyFinancials
from ..models.earnings_calendar import EarningsCalendar
from ..models.investing_chart import InvestingChart


class MyPanels():

	def __init__(self) -> None:
		self.macro_panel = self.macro_panel()
		self.us_panel = self.us_panel()

	def macro_panel(self):
		#Invoke classes holding objects needed for the tab
		investing_chart = InvestingChart(
			chart_height=900,
			chart_width=1600,
		)

		widgets = column(
			investing_chart.primary_axis_header,
			row(
			investing_chart.primary_instrument_selector,
			investing_chart.primary_granularity_selector,
			investing_chart.primary_display_type_selector,
			),
			investing_chart.primary_line_field_selector,
			row(
			investing_chart.primary_ohlc_o_field_selector,
			investing_chart.primary_ohlc_h_field_selector,
			investing_chart.primary_ohlc_l_field_selector,
			investing_chart.primary_ohlc_c_field_selector,
			),
			row(
			investing_chart.primary_bar_top_field_selector,
			),
			investing_chart.primary_axis_portfolio_descriptor,
			row(
			investing_chart.portfolio_open_positions_toggle,
			investing_chart.portfolio_historical_positions_toggle,
			),
			investing_chart.secondary_axis_header,
			row(
			investing_chart.secondary_instrument_selector,
			investing_chart.secondary_granularity_selector,
			investing_chart.secondary_display_type_selector,
			),
			investing_chart.secondary_line_field_selector,
			row(
			investing_chart.secondary_ohlc_o_field_selector,
			investing_chart.secondary_ohlc_h_field_selector,
			investing_chart.secondary_ohlc_l_field_selector,
			investing_chart.secondary_ohlc_c_field_selector,
			),
			row(
			investing_chart.secondary_bar_top_field_selector,
			),
			investing_chart.trigger_calculation_button,
		)
		widgets = self.resize_widgets_column(widgets=widgets)

		#Define layout of tab
		layout = gridplot(
			toolbar_location='left',
			merge_tools=True,
			toolbar_options=dict(logo=None),
			children=[[
			column(widgets),
			column(investing_chart.primary_figure, investing_chart.secondary_figure),
			]]
		)
		return models.TabPanel(
			child=layout,
			title='Macro',
		)

	def us_panel(self):
		#Invoke classes holding objects needed for the tab
		earnings_calendar = EarningsCalendar()
		company_financials = CompanyFinancials()

		#Set object sizes
		company_financials.financials_chart.width = 1000
		company_financials.financials_chart.height = 600
		earnings_calendar.table.height = 600

		widgets = column(
			earnings_calendar.sidebar_title,
			row(
			earnings_calendar.index_selector,
			earnings_calendar.number_of_companies_spinner,
			),
			company_financials.financials_chart_title,
			row(company_financials.company_selector, company_financials.financial_granularity),
			row(
			company_financials.financial_type,
			company_financials.financial_kpi,
			),
			company_financials.date_range,
		)
		widgets = self.resize_widgets_column(widgets=widgets)

		#Define layout of tab
		second_column = column(earnings_calendar.table)
		third_column = column(company_financials.financials_chart,)
		layout = gridplot(
			toolbar_location='left',
			merge_tools=True,
			toolbar_options=dict(logo=None),
			children=[[
			widgets,
			second_column,
			third_column,
			]]
		)

		#Return panel
		return models.TabPanel(
			child=layout,
			title='US',
		)

	def resize_widgets_column(self, widgets: column, widgets_column_width: int = 300):
		for _row in widgets.children:
			if isinstance(_row, models.Row):
				_row_children_width = widgets_column_width / len(_row.children) - len(_row.children) * 2
				for _row_child in _row.children:
					_row_child.width = int(_row_children_width)
			else:
				_row.width = widgets_column_width

		return widgets