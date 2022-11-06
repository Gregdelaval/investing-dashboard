from .panels.panels import MyPanels
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Put panels into tabs
us_panel = MyPanels().us_panel()
tabs = Tabs(tabs=[us_panel])

# Put the tabs in the current document for display
curdoc().add_root(tabs)