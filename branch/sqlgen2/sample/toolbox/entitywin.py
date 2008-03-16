from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

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

class NewTagItem(BaseItem):
    def __init__(self):
        BaseItem.__init__(self, 'New Tag', 'add', 'Create a new tag', 'Create a new tag')

class NewTagAction(BaseAction):
    def __init__(self, slot, parent):
        BaseAction.__init__(self, NewTagItem(), slot, parent, name='NewTagAction')


class MainEntityWindow(KMainWindow):
    def __init__(self, parent):
        KMainWindow.__init__(self, parent, 'Uncover Truth Frontend')
        self.app = get_application_pointer()
        self.main_toolbox_window = parent
        self.splitView = QSplitter(self, 'splitView')
        self.listView = KListView(self.splitView, 'entities_view')
        self.textView = InfoPart(self.splitView)
        #self._sortby = 'name'
        self.initlistView()

        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.connect(self.textView,
                     PYSIGNAL('EntityInfoUpdated'), self.refreshDisplay)
        self.setCentralWidget(self.splitView)

        collection = self.actionCollection()
        #self.quitAction = KStdAction.quit(self.close, collection)
        self.quitAction = KStdAction.quit(self.main_toolbox_window.systray.toggleActive,
                                          collection)
        self.newEntityAction = KStdAction.openNew(self.slotNewEntity, collection)
        self.selectAllAction = KStdAction.selectAll(self.slotSelectAll,
                                                    collection)
        self.newTagAction = NewTagAction(self.slotNewTag, collection)
        
        mainmenu = KPopupMenu(self)
        self.newEntityAction.plug(mainmenu)
        self.newTagAction.plug(mainmenu)
        self.selectAllAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

        toolbar = self.toolBar()
        self.newEntityAction.plug(toolbar)
        self.newTagAction.plug(toolbar)
        self.quitAction.plug(toolbar)

        # dialogs
        self._new_entity_dlg = None
        
        # resize window
        self.resize(400, 500)
        self.splitView.setSizes([75, 325])


    def initlistView(self):
        self.listView.addColumn('entity', -1)
        #self.listView.setSorting(-1)
        self.refreshListView()

    def refreshListView(self):
        self.listView.clear()
        cursor = self.app.conn.stmtcursor()
        rows = self.app.db.get_entities()
        for row in rows:
            #name = '%s %s' % (row.firstname, row.lastname)
            #item = KListViewItem(self.listView, name)
            #item.guestid = row['guestid']
            #item = GuestListViewItem(self.listView, row)
            item = KListViewItem(self.listView, row['name'])
            item.entityid = row['entityid']

    def slotNewEntity(self):
        #win = BaseEntityDialog(self)
        win = MainEntityDialog(self, dtype='insert')
        self._new_entity_dlg = win
        win.show()
        #KMessageBox.information(self, 'add new entity')

    def slotNewTag(self):
        dlg = NewTagDialog(self)
        dlg.show()
        
    def slotSelectAll(self):
        self.textView.view_all_guests()

    def slotSortByName(self):
        self._sortby = 'name'
        self.refreshListView()

    def slotSortByAppearance(self):
        self._sortby = 'guestid'
        self.refreshListView()

    def _new_entity_added(self):
        dlg = self._new_entity_dlg
        if dlg is not None:
            data = dlg.get_data()
            self.app.db.create_entity(data)
            self.refreshListView()
            self._new_entity_dlg = None
            
    def selectionChanged(self):
        item = self.listView.currentItem()
        entityid = item.entityid
        self.textView.set_info(item.entityid)
                
    def refreshDisplay(self):
        #KMessageBox.error(self, 'ack refreshDisplay called')
        #self.refreshListView()
        self.selectionChanged()
        
        
