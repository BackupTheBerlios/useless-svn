from qt import SIGNAL, PYSIGNAL
from qt import QLabel
from qt import QStringList
from qt import QUriDrag

from kdeui import KMainWindow
from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from useless.kdebase.actions import BaseItem, BaseAction
from useless.kdebase.mainwin import BaseMainWindow

from base import get_application_pointer
from infopart import InfoPart

from actions import NewEntityWindowAction, NewRadioWindowAction


from entitywin import MainEntityWindow
from radiowin import BaseRadioWindow
from dropcatcher import MainDropCatcher

# systray test
from kdecore import KIcon, KIconLoader
from kdeui import KSystemTray

class MySytemTray(KSystemTray):
    def __init__(self, parent):
        KSystemTray.__init__(self, parent)
        self.mainwin = parent
        icons = KIconLoader()
        self.setPixmap(icons.loadIcon('edit', KIcon.Desktop, 22))

class MainWindow(BaseMainWindow, MainDropCatcher):
    def __init__(self, parent):
        BaseMainWindow.__init__(self, parent, 'ToolboxMainWindow')
        self.label = QLabel('toobox', self)
        self.setCentralWidget(self.label)
        self.app.main_window = self
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
        self.systray = MySytemTray(self)
        systray_menu = self.systray.contextMenu()
        self.newEntityWindowAction.plug(systray_menu)
        self.newRadioWindowAction.plug(systray_menu)
        
        self.setAcceptDrops(True)
        
            
        self.connect(self.app,
                     PYSIGNAL('UrlHandled'), self.url_handled)
        #self.connect(self, SIGNAL('quit()'), self.hide)
        self._child_windows = dict()
        

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.hide, collection)
        self.newEntityWindowAction = NewEntityWindowAction(self.slotNewEntityWindow,
                                                            collection)
        self.newRadioWindowAction = NewRadioWindowAction(self.slotNewRadioWindow,
                                                         collection)

    def initMenus(self):
        mainmenu = KPopupMenu(self)
        self.newEntityWindowAction.plug(mainmenu)
        self.newRadioWindowAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newEntityWindowAction.plug(toolbar)
        self.newRadioWindowAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def _slotNewWindow(self, winclass):
        count = 1
        name = '%s-%d' % (winclass.__name__, count)
        while self._child_windows.has_key(name):
            count += 1
            name = '%s-%d' % (winclass.__name__, count)
        win = winclass(self, name=name)
        win.show()
        self._child_windows[name] = win
        

    def slotNewEntityWindow(self):
        self._slotNewWindow(MainEntityWindow)

    def slotNewRadioWindow(self):
        self._slotNewWindow(BaseRadioWindow)
        

    def url_handled(self):
        urls = self.app.urlhandler.completed_urls()
        text = ''
        for url in urls:
            if url.host.endswith('youtube.com'):
                if not text:
                    text = "Youtube information\n"
                    text += '---------------------\n'
                data = self.app.urlhandler.retrieve_data(url)
                data['name'] = data['title']
                data['type'] = 'youtube-video'
                data['desc'] = 'Youtube video'
                data['url'] = url
                self.app.db.create_entity(data)
                text += 'Title: %s\n' % data['title']
                text += 'Url for flv file: %s\n' % data['flv_url']
                text += '\n'
        urls = self.app.urlhandler.completed_urls()
        if urls:
            text += 'Unknown urls\n'
        for url in urls:
            text += '%s\n' % url
        KMessageBox.information(self, text)

    def show(self):
        for name, window in self._child_windows.items():
            window.show()
        BaseMainWindow.show(self)

    def hide(self):
        for name, window in self._child_windows.items():
            window.hide()
        BaseMainWindow.hide(self)
        
