from bokeh.io import curdoc
from bokeh.models import Tabs

from .panels.company_financials import CompanyFinancials
from .panels.portfolio import Portfolio
from .panels.earnings_calendar import EarningsCalendar

# Put panels into tabs
_tabs = [
	CompanyFinancials().panel,
	EarningsCalendar().panel,
	Portfolio().panel,
]
tabs = Tabs(tabs=_tabs, styles={'color': 'white'})

# Put the tabs in the current document for display
curdoc().add_root(tabs)
