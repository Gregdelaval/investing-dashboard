from .panels.panels import MyPanels
from bokeh.io import curdoc
from bokeh.models import Tabs

# Put panels into tabs
Panels = MyPanels()
tabs = Tabs(tabs=[Panels.macro_panel, Panels.us_panel])

# Put the tabs in the current document for display
curdoc().add_root(tabs)