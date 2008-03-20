from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu
from kdeui import KComboBox

from useless.kdebase.mainwin import BaseMainWindow
from useless.kdebase.dialogs import SimpleEntryDialog

class NewEntityTypeDialog(SimpleEntryDialog):
    def __init__(self, parent, name='NewEntityTypeDialog'):
        label = "Enter a new entity type"
        SimpleEntryDialog.__init__(self, parent, label=label, name=name)

    def ok_clicked(self):
        etype = self._get_entry().strip()
        if etype:
            self.app.db.create_entity_type(etype)
            self.parent().refreshListView()
        
class NewExtraFieldDialog(SimpleEntryDialog):
    def __init__(self, parent, etype, name='NewExtraFieldDialog'):
        label = "Enter a new extra field for entity type %s" % etype
        SimpleEntryDialog.__init__(self, parent, label=label, name=name)
        self.combo = KComboBox(self.frame)
        types = ['name', 'bool', 'int', 'url', 'text']
        self.combo.insertStrList(types)
        self.etype = etype
        self.vbox.addWidget(self.combo)
        
    def ok_clicked(self):
        fieldname = self._get_entry().strip()
        fieldtype = str(self.combo.currentText())
        if fieldname:        
            self.app.db.create_extra_field(self.etype, fieldname, fieldtype=fieldtype)
        
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
        self.current_etype = None
        
        

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
        self.extfieldsView.addColumn('fieldname')
        self.extfieldsView.addColumn('fieldtype')
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
        self.current_etype = etype
        fields = self.app.db.get_etype_extra_fields(etype)
        self.extfieldsView.clear()
        for field in fields:
            item = KListViewItem(self.extfieldsView, *field)
            item.fieldname = field[0]
            
            
    def slotNewEntityType(self):
        dlg = NewEntityTypeDialog(self)
        dlg.show()

    def slotNewExtraField(self):
        if self.current_etype is not None:
            dlg = NewExtraFieldDialog(self, self.current_etype)
            dlg.show()
