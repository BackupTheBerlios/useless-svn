import os

# we use string.ascii_letters and string.digits
# from the string module
import string

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
from actions import NewRtorrentWindowAction


from entitywin import MainEntityWindow
from radiowin import BaseRadioWindow
from dropcatcher import MainDropCatcher
from rtorrent.mainwin import BaseRtorrentWindow

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

        
        self.setAcceptDrops(True)
        self.connect(self.app,
                     PYSIGNAL('UrlHandled'), self.url_handled)
        #self.connect(self, SIGNAL('quit()'), self.hide)
        self._child_windows = dict()

        if os.environ.has_key('DEBUG') and os.environ['DEBUG'] == 'nosystray':
            self.systray = self
        else:
            self.systray = MySytemTray(self)
            systray_menu = self.systray.contextMenu()
            self.newEntityWindowAction.plug(systray_menu)
            self.newRadioWindowAction.plug(systray_menu)
        

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.hide, collection)
        self.newEntityWindowAction = NewEntityWindowAction(self.slotNewEntityWindow,
                                                            collection)
        self.newRadioWindowAction = NewRadioWindowAction(self.slotNewRadioWindow,
                                                         collection)
        self.newRtorrentWindowAction = NewRtorrentWindowAction(self.slotNewRtorrentWindow,
                                                               collection)
        
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        self.newEntityWindowAction.plug(mainmenu)
        self.newRadioWindowAction.plug(mainmenu)
        self.newRtorrentWindowAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newEntityWindowAction.plug(toolbar)
        self.newRadioWindowAction.plug(toolbar)
        self.newRtorrentWindowAction.plug(toolbar)
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
        
    def slotNewRtorrentWindow(self):
        self._slotNewWindow(BaseRtorrentWindow)
        
    def _make_youtube_dl_filename(self, youtubeid, title):
        title = ''.join(x in string.ascii_letters + string.digits and x or '_' for x in title)
        title = title.replace(' ', '_')
        # determine filename
        filename = '%s-%s.flv' % (title, youtubeid)
        return filename
    
    def url_handled(self):
        urls = self.app.urlhandler.completed_urls()
        for url in urls:
            if url.host.endswith('youtube.com'):
                download = False
                main = dict()
                data = self.app.urlhandler.retrieve_data(url)
                if data.has_key('entityid') and data['entityid'] is None:
                    main['name'] = data['title']
                    main['type'] = 'youtube-video'
                    main['desc'] = 'Youtube video'
                    main['url'] = url
                    extras = dict()
                    extras['youtubeid'] = data['youtubeid']
                    # default to not there
                    extras['local-copy'] = False
                    # normalize title similar to youtube-dl
                    filename = self._make_youtube_dl_filename(data['youtubeid'], data['title'])
                    # add filename to extras
                    extras['local-filename'] = filename
                    # create entity
                    dbdata = dict(main=main, extras=extras, tags=list())
                    self.app.db.create_entity(dbdata)
                    download = True
                else:
                    entityid = data['entityid']
                    lc = self.app.db.get_extra_field_data(entityid, 'local-copy')
                    
                    if lc == 'False':
                        download = True
                        filename = self.app.db.get_extra_field_data(entityid, 'local-filename')
                if download:
                    # download youtube video
                    self.app.filehandler.download(data['flv_url'], filename)
                
        msg = "handled url %s" % ',\n '.join(list(urls))
        KMessageBox.information(self, msg)

    def show(self):
        for name, window in self._child_windows.items():
            window.show()
        BaseMainWindow.show(self)

    def hide(self):
        if self.systray is self:
            BaseMainWindow.close(self)
        else:
            for name, window in self._child_windows.items():
                window.hide()
            BaseMainWindow.hide(self)
        
