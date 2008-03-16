from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KMainWindow
from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from useless.kdebase.actions import BaseItem, BaseAction

from utbase import get_application_pointer
from utinfo import InfoPart

from utdialogs import BaseGuestDialog

sortbyappearance_guiitem = BaseItem('Sort by Appearance', 'sort',
                                    'Sort by Appearance', 'Sort by Appearance')
sortbyname_guiitem = BaseItem('Sort by Name', 'sort',
                              'Sort by Name', 'Sort by Name')

class SortByAppearanceAction(BaseAction):
    def __init__(self, slot, parent, name='SortByAppearanceAction'):
        BaseAction.__init__(self, sortbyappearance_guiitem,
                            slot, parent, name=name)

class SortByNameAction(BaseAction):
    def __init__(self, slot, parent, name='SortByNameAction'):
        BaseAction.__init__(self, sortbyname_guiitem,
                            slot, parent, name=name)
        

class GuestListViewItem(KListViewItem):
    def __init__(self, parent, row):
        name = '%s %s' % (row.firstname, row.lastname)
        KListViewItem.__init__(self, parent, name)
        self.guestid = row['guestid']
        #self._sortby = 'guestid'
        self._sortby = 'name'
        
    def key(self, column, ascending):
        if self._sortby == 'guestid':
            text = '%08d' % self.guestid
            return text
        else:
            return KListViewItem.key(self, column, ascending)

    def sortbyGuestID(self):
        self._sortby = 'guestid'

    def sortbyName(self):
        self._sortby = 'name'

    
class MainWindow(KMainWindow):
    def __init__(self, parent):
        KMainWindow.__init__(self, parent, 'Uncover Truth Frontend')
        self.app = get_application_pointer()
        self.splitView = QSplitter(self, 'splitView')
        self.listView = KListView(self.splitView, 'guests_view')
        self.textView = InfoPart(self.splitView)
        self._sortby = 'name'
        self.initlistView()

        self.connect(self.listView,
                     SIGNAL('selectionChanged()'), self.selectionChanged)
        self.connect(self.textView,
                     PYSIGNAL('GuestInfoUpdated'), self.refreshDisplay)
        self.setCentralWidget(self.splitView)

        collection = self.actionCollection()
        self.quitAction = KStdAction.quit(self.close, collection)
        self.newGuestAction = KStdAction.openNew(self.slotNewGuest, collection)
        self.selectAllAction = KStdAction.selectAll(self.slotSelectAll,
                                                    collection)
        self.sortbyNameAction = SortByNameAction(self.slotSortByName, collection)
        self.sortbyAppearanceAction = SortByAppearanceAction(self.slotSortByAppearance,
                                                             collection)
        mainmenu = KPopupMenu(self)
        self.newGuestAction.plug(mainmenu)
        self.selectAllAction.plug(mainmenu)
        self.sortbyNameAction.plug(mainmenu)
        self.sortbyAppearanceAction.plug(mainmenu)
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

        toolbar = self.toolBar()
        self.newGuestAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
        self.new_guest_dialog = None

        # resize window
        self.resize(400, 500)
        self.splitView.setSizes([75, 325])

    def initlistView(self):
        self.listView.addColumn('guests', -1)
        #self.listView.setSorting(-1)
        self.refreshListView()

    def refreshListView(self):
        self.listView.clear()
        cursor = self.app.conn.stmtcursor()
        rows = self.app.guests.get_guest_rows()
        for row in rows:
            #name = '%s %s' % (row.firstname, row.lastname)
            #item = KListViewItem(self.listView, name)
            #item.guestid = row['guestid']
            item = GuestListViewItem(self.listView, row)
            if self._sortby == 'guestid':
                item.sortbyGuestID()
            else:
                item.sortbyName()
    
    def slotNewGuest(self):
        win = BaseGuestDialog(self)
        self.connect(win, SIGNAL('okClicked()'),
                     self._new_guest_added)
        self.new_guest_dialog = win
        win.show()
    
    def slotSelectAll(self):
        self.textView.view_all_guests()

    def slotSortByName(self):
        self._sortby = 'name'
        self.refreshListView()

    def slotSortByAppearance(self):
        self._sortby = 'guestid'
        self.refreshListView()
    
    def _new_guest_added(self):
        dlg = self.new_guest_dialog
        if dlg is not None:
            data = dlg.get_guest_data()
            self.app.guests.insert_guest_data(data)
            self.refreshListView()
            self.new_guest_dialog = None
            
    def selectionChanged(self):
        item = self.listView.currentItem()
        guestid = item.guestid
        self.textView.set_guest_info(item.guestid)

    def refreshDisplay(self):
        #KMessageBox.error(self, 'ack refreshDisplay called')
        #self.refreshListView()
        self.selectionChanged()
        
        
