from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from windows import BaseToolboxWindow
from dropcatcher import MainDropCatcher

from actions import NewTagAction
from infopart import RtorrentInfoPart

from dialogs import MainEntityDialog
from dialogs import NewTagDialog

from xmlrpc import Rtorrent, Server


class BaseRtorrentWindow(BaseToolboxWindow, MainDropCatcher):
    def __init__(self, parent, name='MainEntityWindow'):
        BaseToolboxWindow.__init__(self, parent, name=name)
        self.splitView = QSplitter(self, 'splitView')
        self.listView = KListView(self.splitView, 'entities_view')
        self.textView = RtorrentInfoPart(self.splitView)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
        self.app.rtserver = Server(url="http://roujin/RPC2")
        self.app.rtorrent = Rtorrent(self.app.rtserver)

        #self._sortby = 'name'
        self.initlistView()

        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.connect(self.textView,
                     PYSIGNAL('EntityInfoUpdated'), self.refreshDisplay)
        self.setCentralWidget(self.splitView)

        
        # dialogs
        self._new_entity_dlg = None
        
        # resize window
        self.resize(400, 500)
        self.splitView.setSizes([75, 325])

        self.setAcceptDrops(True)
        
    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newEntityAction = KStdAction.openNew(self.slotNewEntity, collection)
        self.newTagAction = NewTagAction(self.slotNewTag, collection)
        self.manageEntityTypesAction = KStdAction.addBookmark(self.slotManageEntityTypes,
                                                              collection)
        
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        self.newEntityAction.plug(mainmenu)
        self.newTagAction.plug(mainmenu)
        self.manageEntityTypesAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

    def initToolbar(self):
        toolbar = self.toolBar()
        self.newEntityAction.plug(toolbar)
        self.newTagAction.plug(toolbar)
        self.manageEntityTypesAction.plug(toolbar)
        self.quitAction.plug(toolbar)

    def initlistView(self):
        self.listView.addColumn('entity', -1)
        #self.listView.setSorting(-1)
        self.refreshListView()

    def refreshListView(self):
        self.listView.clear()
        torrents = self.app.rtorrent.torrents
        for k, v in self.app.rtorrent.torrents.items():
            item = KListViewItem(self.listView, v.name)
            item.infohash = k

    def slotNewEntity(self):
        from dialogs import SelectEntityTypeDialog
        win = SelectEntityTypeDialog(self)
        
        #win = MainEntityDialog(self, dtype='insert')
        #self._new_entity_dlg = win
        win.show()

    def slotNewTag(self):
        dlg = NewTagDialog(self)
        dlg.show()
        
    def slotManageEntityTypes(self):
        win = EntityTypeWindow(self)
        win.show()
    
    def _new_entity_added(self):
        dlg = self._new_entity_dlg
        if dlg is not None:
            data = dlg.get_data()
            self.app.db.create_entity(data)
            self.refreshListView()
            self._new_entity_dlg = None
            
    def selectionChanged(self):
        item = self.listView.currentItem()
        infohash = item.infohash
        tv = self.textView
        self.textView.set_info(infohash)
                
    def refreshDisplay(self):
        #KMessageBox.error(self, 'ack refreshDisplay called')
        #self.refreshListView()
        self.selectionChanged()

