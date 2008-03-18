from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from windows import BaseToolboxWindow

from infopart import InfoPart
#from dialogs import BaseEntityDialog
from dialogs import MainEntityDialog
from dialogs import NewTagDialog

class BaseRadioWindow(BaseToolboxWindow):
    def __init__(self, parent, name='BaseMainWindow'):
        BaseToolboxWindow.__init__(self, parent, name=name)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
        # resize window
        self.resize(400, 500)
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newStationAction = KStdAction.openNew(self.slotNewStation, collection)

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        self.newStationAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
        menubar.insertItem('&Help', self.helpMenu(''))

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newStationAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def slotNewStation(self):
        pass
