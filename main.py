from .panels.panels import MyPanels
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from .helpers.helpers import Helpers

print('\n')
#Boot operatios
Helpers().load_variables(root='//'.join(__file__.replace('\\', '//').split('//')[0:-1]) + '//',)
Helpers().clear_cache()

# Put panels into tabs
us_panel = MyPanels().us_panel()
tabs = Tabs(tabs=[us_panel])

# Put the tabs in the current document for display
curdoc().add_root(tabs)