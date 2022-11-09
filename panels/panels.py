from bokeh.layouts import gridplot, column
from bokeh import models
from ..models.company_financials import CompanyFinancials
from ..models.earnings_calendar import EarningsCalendar
from ..models.investing_chart import InvestingChart


class MyPanels():

	def us_panel(self):
		#Invoke classes holding objects needed for the tab
		investing_chart = InvestingChart()

		#Set object sizes
		investing_chart.figure.width = 1800
		investing_chart.figure.height = 800

		#Define layout of tab
		layout = gridplot(
			toolbar_location='left',
			merge_tools=True,
			toolbar_options=dict(logo=None),
			children=[[
			column(
			investing_chart.figure,
			investing_chart.granularity_selector,
			investing_chart.instrument_selector,
			investing_chart.portfolio_checkbox_group,
			)
			]]
		)
		# #Invoke classes holding objects needed for the tab
		# earnings_calendar = EarningsCalendar()
		# company_financials = CompanyFinancials()
		# investing_chart = InvestingChart()

		# #Set object sizes
		# company_financials.financials_chart.width = 1000
		# company_financials.financials_chart.height = 600
		# earnings_calendar.table.height = 600
		# investing_chart.test_figure.width = 1600

		# #Define layout of tab
		# first_column = column(
		# 	earnings_calendar.sidebar_title,
		# 	earnings_calendar.index_description,
		# 	earnings_calendar.index_selector,
		# 	earnings_calendar.number_of_companies_description,
		# 	earnings_calendar.number_of_companies_spinner,
		# 	company_financials.financials_chart_title,
		# 	company_financials.company_selector_description,
		# 	company_financials.company_selector,
		# 	company_financials.financial_type_description,
		# 	company_financials.financial_type,
		# 	company_financials.financial_kpi_description,
		# 	company_financials.financial_kpi,
		# 	company_financials.financial_granularity_description,
		# 	company_financials.financial_granularity,
		# 	company_financials.date_range_description,
		# 	company_financials.date_range,
		# )
		# second_column = column(investing_chart.test_figure, earnings_calendar.table)
		# third_column = column(company_financials.financials_chart,)
		# layout = gridplot(
		# 	toolbar_location='left',
		# 	merge_tools=True,
		# 	toolbar_options=dict(logo=None),
		# 	children=[[
		# 	first_column,
		# 	second_column,
		# 	third_column,
		# 	]]
		# )

		#Return panel
		return models.Panel(
			child=layout,
			title='US',
		)