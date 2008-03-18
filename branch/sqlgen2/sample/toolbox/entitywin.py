from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KMainWindow
from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from useless.kdebase.mainwin import BaseMainWindow

from windows import BaseToolboxWindow

from actions import NewTagAction
from infopart import InfoPart
#from dialogs import BaseEntityDialog
from dialogs import MainEntityDialog
from dialogs import NewTagDialog

class EntityTypeWindow(BaseMainWindow):
    def __init__(self, parent, name='EntityTypeWindow'):
        BaseMainWindow.__init__(self, parent, name=name)
        self.splitView = QSplitter(self, 'splitView')
        self.etypeView = KListView(self.splitView, 'etypes_view')
        self.extfieldsView = KListView(self.splitView, 'extfields_view')
        self.initActions()
        self.initMenus()
        self.initToolbar()
        self.setCentralWidget(self.splitView)
        self.connect(self.etypeView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.initlistView()
        
        

    def initActions(self):
        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newEntityTypeAction = KStdAction.openNew(self.slotNewEntityType, collection)
        self.newExtraFieldAction = KStdAction.addBookmark(self.slotNewExtraField, collection)
        
    def initMenus(self):
        mainmenu = KPopupMenu(self)
        self.newEntityTypeAction.plug(mainmenu)
        self.newExtraFieldAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)
                
    def initToolbar(self):
        toolbar = self.toolBar()
        self.newEntityTypeAction.plug(toolbar)
        self.newExtraFieldAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
    def initlistView(self):
        self.etypeView.addColumn('entity type', -1)
        self.extfieldsView.addColumn('extra field', -1)
        self.refreshListView()

    def refreshListView(self):
        self.etypeView.clear()
        etypes = self.app.db.get_entity_types()
        for etype in etypes:
            item = KListViewItem(self.etypeView, etype)
            item.etype = etype
        
    def selectionChanged(self):
        item = self.etypeView.currentItem()
        etype = item.etype
        fields = self.app.db.get_extra_fields(etype)
        self.extfieldsView.clear()
        for field in fields:
            item = KListViewItem(self.extfieldsView, field)
            item.fieldname = field
            
    def slotNewEntityType(self):
        print 'in slotNewEntityType'

    def slotNewExtraField(self):
        print 'in slotNewExtraField'
        
    
class MainEntityWindow(BaseToolboxWindow):
    def __init__(self, parent, name='MainEntityWindow'):
        BaseToolboxWindow.__init__(self, parent, name=name)
        self.splitView = QSplitter(self, 'splitView')
        self.listView = KListView(self.splitView, 'entities_view')
        self.textView = InfoPart(self.splitView)
        self.initActions()
        self.initMenus()
        self.initToolbar()
        
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
        self.quitAction.plug(toolbar)

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
        entityid = item.entityid
        self.textView.set_info(item.entityid)
                
    def refreshDisplay(self):
        #KMessageBox.error(self, 'ack refreshDisplay called')
        #self.refreshListView()
        self.selectionChanged()

