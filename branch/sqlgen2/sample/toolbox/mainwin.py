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

from base import get_application_pointer
from infopart import InfoPart
#from dialogs import BaseEntityDialog
from dialogs import MainEntityDialog
from dialogs import NewTagDialog
from entitywin import MainEntityWindow
from radiowin import BaseRadioWindow
from dropcatcher import MainDropCatcher

# systray test
from kdecore import KIcon, KIconLoader
from kdeui import KSystemTray

class NewTagItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'New Tag', 'add', 'Create a new tag', 'Create a new tag')

class NewTagAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, NewTagItem(), slot, parent, name='NewTagAction')

class MySytemTray(KSystemTray):
    def __init__(self, parent):
        KSystemTray.__init__(self, parent)
        self.mainwin = parent
        icons = KIconLoader()
        self.setPixmap(icons.loadIcon('edit', KIcon.Desktop, 22))
        collection = self.actionCollection()
        menu = self.contextMenu()
        menu.insertItem('Entity Window')
        menu.insertItem('Radio Window')
        self.connect(menu, SIGNAL('activated(int)'), self.item_activated)
        self._child_windows = dict()

    def item_activated(self, index):
        text = self.contextMenu().text(index)
        print 'item_activated', text
        if text == 'Entity Window':
            count = 1
            name = 'MainEntityWindow-%d' % count
            while self._child_windows.has_key(name):
                count += 1
                name = 'MainEntityWindow-%d' % count
            win = MainEntityWindow(self.mainwin, name=name)
            win.show()
            self._child_windows[name] = win
        elif text == 'Radio Window':
            count = 1
            name = 'BaseRadioWindow-%d' % count
            while self._child_windows.has_key(name):
                count += 1
                name = 'BaseRadioWindow-%d' % count
            win = BaseRadioWindow(self.mainwin, name=name)
            win.show()
            self._child_windows[name] = win
            
        
class MainWindow(KMainWindow, MainDropCatcher):
    def __init__(self, parent):
        KMainWindow.__init__(self, parent, 'Uncover Truth Frontend')
        self.app = get_application_pointer()
        self.label = QLabel('toobox', self)
        self.setCentralWidget(self.label)
        self.app.main_window = self
        self.systray = MySytemTray(self)
        self.setAcceptDrops(True)
        
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.systray.toggleActive, collection)
        
        mainmenu = KPopupMenu(self)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

        toolbar = self.toolBar()
        self.quitAction.plug(toolbar)

        self.connect(self.app,
                     PYSIGNAL('UrlHandled'), self.url_handled)

    def url_handled(self):
        urls = self.app.urlhandler.completed_urls()
        text = ''
        for url in urls:
            if url.host.endswith('youtube.com'):
                if not text:
                    text = "Youtube information\n"
                    text += '---------------------\n'
                data = self.app.urlhandler.retrieve_data(url)
                dbdata = dict(name=data['title'], url=url, desc="youtube video")
                self.app.db.create_entity(dbdata)
                text += 'Title: %s\n' % data['title']
                text += 'Url for flv file: %s\n' % data['flv_url']
                text += '\n'
        urls = self.app.urlhandler.completed_urls()
        if urls:
            text += 'Unknown urls\n'
        for url in urls:
            text += '%s\n' % url
        KMessageBox.information(self, text)
