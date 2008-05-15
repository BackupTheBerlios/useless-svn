from qt import SIGNAL, PYSIGNAL
from qt import QSplitter

from kdeui import KMainWindow
from kdeui import KListView, KListViewItem
from kdeui import KMessageBox
from kdeui import KStdAction
from kdeui import KPopupMenu

from kfile import KDirSelectDialog, KFileDialog


from useless.base.path import path
from useless.kdebase.actions import BaseItem, BaseAction

from utbase import get_application_pointer
from utinfo import InfoPart

from utdialogs import BaseGuestDialog

sortbyappearance_guiitem = BaseItem('Sort by Appearance', 'sort',
                                    'Sort by Appearance', 'Sort by Appearance')
sortbyname_guiitem = BaseItem('Sort by Name', 'sort',
                              'Sort by Name', 'Sort by Name')

import_guiitem = BaseItem('Import Guest', 'fileimport',
                          'Import Guest', 'Import Guest')

export_guiitem = BaseItem('Export Guest', 'fileexport',
                          'Export Guest', 'Export Guest')

exportall_guiitem = BaseItem('Export All Guests', 'save_all',
                             'Export All Guests', 'Export All Guests')

importall_guiitem = BaseItem('Import a Directory', 'fill',
                             'Import a Directory', 'Import a Directory')

class SortByAppearanceAction(BaseAction):
    def __init__(self, slot, parent, name='SortByAppearanceAction'):
        BaseAction.__init__(self, sortbyappearance_guiitem,
                            slot, parent, name=name)

class SortByNameAction(BaseAction):
    def __init__(self, slot, parent, name='SortByNameAction'):
        BaseAction.__init__(self, sortbyname_guiitem,
                            slot, parent, name=name)
        
class ImportGuestAction(BaseAction):
    def __init__(self, slot, parent, name='ImportGuestAction'):
        BaseAction.__init__(self, import_guiitem,
                            slot, parent, name=name)

class ExportGuestAction(BaseAction):
    def __init__(self, slot, parent, name='ExportGuestAction'):
        BaseAction.__init__(self, export_guiitem,
                            slot, parent, name=name)
        
class ExportAllGuestsAction(BaseAction):
    def __init__(self, slot, parent, name='ExportAllGuestsAction'):
        BaseAction.__init__(self, exportall_guiitem,
                            slot, parent, name=name)

class ImportAllGuestsAction(BaseAction):
    def __init__(self, slot, parent, name='ImportAllGuestsAction'):
        BaseAction.__init__(self, importall_guiitem,
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
        self.file_filter = '*.xml|XML Files\n*|All Files'
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
        self.importGuestAction = ImportGuestAction(self.slotImportGuest, collection)
        self.exportGuestAction = ExportGuestAction(self.slotExportGuest, collection)
        self.exportAllGuestsAction = ExportAllGuestsAction(self.slotExportAllGuests,
                                                           collection)
        self.importAllGuestsAction = ImportAllGuestsAction(self.slotImportAllGuests,
                                                           collection)
        
        mainmenu = KPopupMenu(self)
        self.newGuestAction.plug(mainmenu)
        self.selectAllAction.plug(mainmenu)
        mainmenu.insertSeparator()
        self.sortbyNameAction.plug(mainmenu)
        self.sortbyAppearanceAction.plug(mainmenu)
        mainmenu.insertSeparator()
        self.importGuestAction.plug(mainmenu)
        self.exportGuestAction.plug(mainmenu)
        self.importAllGuestsAction.plug(mainmenu)
        self.exportAllGuestsAction.plug(mainmenu)
        mainmenu.insertSeparator()
        self.quitAction.plug(mainmenu)
        menubar = self.menuBar()
        menubar.insertItem('&Main', mainmenu)

        toolbar = self.toolBar()
        self.newGuestAction.plug(toolbar)
        self.importGuestAction.plug(toolbar)
        self.exportGuestAction.plug(toolbar)
        self.quitAction.plug(toolbar)
        
        self.new_guest_dialog = None
        self.file_dialog = None

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
    
    def slotImportGuest(self):
        if self.file_dialog is None:
            win = KFileDialog('.', self.file_filter, self,
                              'import_guest_dialog', True)
            win.show()
        
    def slotImportAllGuests(self):
        if self.file_dialog is None:
            win = KDirSelectDialog('.', 0, self)
            win.connect(win, SIGNAL('okClicked()'), self.import_directory_selected)
            win.connect(win, SIGNAL('cancelClicked()'), self.destroy_file_dialog)
            win.connect(win, SIGNAL('closeClicked()'), self.destroy_file_dialog)
            win.show()
            self.file_dialog = win

    
    def slotExportGuest(self):
        item = self.listView.currentItem()
        guestid = item.guestid
        filename = self._guest_xmlfilename(guestid)
        win = KFileDialog(filename, self.file_filter, self, 'export_guest_dialog', True)
        win.connect(win, SIGNAL('okClicked()'), self.export_filename_selected)
        win.connect(win, SIGNAL('cancelClicked()'), self.destroy_file_dialog)
        win.connect(win, SIGNAL('closeClicked()'), self.destroy_file_dialog)
        win.guestid = guestid
        win.show()
        self.file_dialog = win
        

    def _guest_xmlfilename(self, guestid):
        data = self.app.guests.get_guest_data(guestid)
        filename = '%s_%s.xml' % (data['firstname'].lower(), data['lastname'].lower())
        return filename
    
    def export_guest(self, guestid, filename):
        filename = path(filename)
        if filename.isdir():
            filename = filename / self._guest_xmlfilename(guestid)
        xmldata = self.app.guests.export_guest_xml(guestid, self.app.datadir)
        xmlfile = filename.open('w')
        xmlfile.write(xmldata.toxml())
        xmlfile.close()
        
    def import_guest(self, filename):
        self.app.guests.import_guest_xml(filename, self.app.datadir)
        
    def export_filename_selected(self):
        win = self.file_dialog
        url = win.selectedURL()
        fullpath = path(str(url.path()))
        self.export_guest(win.guestid, fullpath)
        self.destroy_file_dialog()
        

    def export_directory_selected(self):
        win = self.file_dialog
        url = win.url()
        fullpath = path(str(url.path()))
        for row in self.app.guests.get_guest_rows():
            self.export_guest(row['guestid'], fullpath)
        self.destroy_file_dialog()
        
    def import_directory_selected(self):
        win = self.file_dialog
        url = win.url()
        fullpath = path(str(url.path()))
        for xmlfile in fullpath.listdir('*.xml'):
            self.import_guest(xmlfile)
        self.destroy_file_dialog()
        
    def slotExportAllGuests(self):
        if self.file_dialog is None:
            win = KDirSelectDialog('.', 0, self)
            win.connect(win, SIGNAL('okClicked()'), self.export_directory_selected)
            win.connect(win, SIGNAL('cancelClicked()'), self.destroy_file_dialog)
            win.connect(win, SIGNAL('closeClicked()'), self.destroy_file_dialog)
            win.show()
            self.file_dialog = win

    def destroy_file_dialog(self):
        self.file_dialog = None
        
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
        
        
