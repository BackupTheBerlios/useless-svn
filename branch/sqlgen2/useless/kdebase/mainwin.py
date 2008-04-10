from qt import QSplitter
from qt import SIGNAL

from kdeui import KMainWindow
from kdeui import KListView
from kdeui import KStdAction
from kdeui import KPopupMenu

from base import get_application_pointer


from error import MethodNotImplementedError

class BaseMainWindow(KMainWindow):
    def __init__(self, parent, name='BaseMainWindow'):
        KMainWindow.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.current_dialog = None

    def connect_dialog(self, window, ok_clicked):
        self.connect(window, SIGNAL('okClicked()'), ok_clicked)
        self.connect_destroy_dialog(window)
        
    def connect_destroy_dialog(self, window):
        self.connect(window, SIGNAL('cancelClicked()'), self.destroy_current_dialog)
        self.connect(window, SIGNAL('closeClicked()'), self.destroy_current_dialog)
        self.current_dialog = window

    def destroy_current_dialog(self):
        self.current_dialog = None
        
    def initActions(self):
        raise MethodNotImplementedError(self, 'initActions not implemented in base class')

    def initMenus(self):
        raise MethodNotImplementedError(self, 'initMenus not implemented in base class')

    def initToolbar(self):
        raise MethodNotImplementedError(self, 'initToolbar not implemented in base class')
    

class SimpleMainWindow(BaseMainWindow):
    def __init__(self, parent, name='SimpleMainWindow'):
        BaseMainWindow.__init__(self, parent, name=name)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
    # in subclass at end of initActions call
    # SimpleMainWindow.initActions(self, collection)
    # to automatically add the quitAction
    def initActions(self, collection=None):
        if collection is None:
            collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)

    # in subclass at end of initMenus call
    # SimpleMainWindow.initMenus(self, mainmenu)
    # to automatically plug the quitAction into the mainmenu
    # and create the help menu
    def initMenus(self, mainmenu=None):
        if mainmenu is None:
            mainmenu = KPopupMenu(self)
        self.quitAction.plug(mainmenu)
        self.menuBar().insertItem('&Main', mainmenu)
        self.menuBar().insertItem('&Help', self.helpMenu(''))
    
class BaseSplitWindow(BaseMainWindow):
    def __init__(self, parent, view, listview=None, name='BaseSplitWIndow'):
        BaseMainWindow.__init__(self, parent, name=name)
        self.splitter = QSplitter(self, 'mainView')
        if listview is None:
            self.listView = KListView(self.splitter)
        else:
            self.listView = listview(self.splitter)
        self.mainView = view(self.splitter)
        self.setCentralWidget(self.splitter)
        if hasattr(self, 'initlistView'):
            self.initlistView()
        elif hasattr(self.listView, 'initlistView'):
            self.listView.initlistView()
        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)

class BaseViewWindow(BaseMainWindow):
    def __init__(self, parent, view, name='BaseViewWindow'):
        BaseMainWindow.__init__(self, parent, name)
        self.view = view(self)
        self.setCentralWidget(self.view)
        
