from qt import Qt, SIGNAL, SLOT, PYSIGNAL
from qt import QFrame
from qt import QLabel, QGridLayout

from kdeui import KLineEdit, KTextEdit
from kdeui import KListView, KListViewItem

from kdeui import KDialogBase
from kdeui import KPushButton
from kdeui import KStdGuiItem

from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseDialogWindow

    
class BaseEntityDataFrame(QFrame):
    def __init__(self, parent, name='BaseEntityDataFrame'):
        QFrame.__init__(self, parent, name)
        self.entityid = None
        numrows = 2
        numcols = 1
        margin = 3
        space = 2
        self.grid = QGridLayout(self, numrows, numcols,
                                margin, space, 'BaseEntityDataLayout')
        self.app = get_application_pointer()


        self.name_lbl = QLabel('Name', self)
        self.name_entry = KLineEdit('', self)

        self.grid.addWidget(self.name_lbl, 0, 0)
        self.grid.addWidget(self.name_entry, 1, 0)

        self.etype_lbl = QLabel('type', self)
        self.etype_entry = KLineEdit('generic', self)

        self.grid.addWidget(self.etype_lbl, 2, 0)
        self.grid.addWidget(self.etype_entry, 3, 0)

        self.url_lbl = QLabel('url', self)
        self.url_entry = KLineEdit('', self)

        self.grid.addWidget(self.url_lbl, 4, 0)
        self.grid.addWidget(self.url_entry, 5, 0)
        

        self.desc_lbl = QLabel('Description', self)
        self.desc_entry = KTextEdit(self, 'description_entry')
        self.desc_entry.setTextFormat(self.PlainText)
        
        self.grid.addMultiCellWidget(self.desc_lbl, 6, 6, 0, 0)
        self.grid.addMultiCellWidget(self.desc_entry, 7, 10, 0, 0)

        #self.works_frame = BaseGuestWorksFrame(self)
        #self.grid.addMultiCellWidget(self.works_frame, 8, 8, 0, 1)


    def get_data(self):
        name = str(self.name_entry.text())
        etype = str(self.etype_entry.text())
        url = str(self.url_entry.text())
        desc = str(self.desc_entry.text())
        data = dict(name=name, type=etype,
                    url=url, desc=desc)
        if self.entityid is not None:
            data['entityid'] = self.entityid
        return data

    def set_data(self, data):
        self.entityid = data['entityid']
        self.name_entry.setText(data['name'])
        self.etype_entry.setText(data['type'])
        self.url_entry.setText(data['url'])
        self.desc_entry.setText(data['desc'])

class BaseEntityDialog(BaseDialogWindow):
    def __init__(self, parent, name='BaseEntityDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.frame = BaseEntityDataFrame(self)
        self.setMainWidget(self.frame)

    def get_data(self):
        return self.frame.get_data()

    def set_data(self, data):
        self.frame.set_data(data)
        
    def insert_entity(self):
        data = self.frame.get_data()
        self.app.db.create_entity(data)

    def update_entity(self):
        data = self.frame.get_data()
        self.app.db.change_entity(self.entityid, data)
        
class MainEntityDialog(BaseEntityDialog):
    def __init__(self, parent, dtype='insert', entityid=None, name='MainEntityDialog'):
        BaseEntityDialog.__init__(self, parent, name=name)
        self.entityid = entityid
        self._dtype = dtype
        if self._dtype == 'insert':
            self.connect(self, SIGNAL('okClicked()'), self.insert_entity)
        elif self._dtype == 'update':
            self.connect(self, SIGNAL('okClicked()'), self.update_entity)
            data = self.app.db.get(self.entityid)
            self.set_data(data)
        else:
            KMessageBox.error(self, "Bad dtype: %s" % dtype)
            

class BaseTagDialogFrame(QFrame):
    def __init__(self, parent, name='BaseEntityDataFrame'):
        QFrame.__init__(self, parent, name)
        self.entityid = None
        numrows = 5
        numcols = 1
        margin = 0
        space = 1
        self.grid = QGridLayout(self, numrows, numcols,
                                margin, space, 'BaseEntityDataLayout')
        self.app = get_application_pointer()

        self.lbl = QLabel('Select the tags', self)
        self.grid.addWidget(self.lbl, 0, 0)

        self.listView = KListView(self)
        self.listView.addColumn('tagname', -1)
        self.listView.clear()
        self.grid.addMultiCellWidget(self.listView, 1, 4, 0, 0)

class BaseTagsDialog(BaseDialogWindow):
    def __init__(self, parent, entityid, name='BaseTagsDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.entityid = entityid
        self.frame = BaseTagDialogFrame(self)
        self.setMainWidget(self.frame)
        #import pdb
        #pdb.set_trace()
        self.frame.listView.setSelectionModeExt(KListView.Extended)
        
class AddTagsDialog(BaseTagsDialog):
    def __init__(self, parent, entityid, name='AddTagsDialog'):
        BaseTagsDialog.__init__(self, parent, entityid, name=name)
        sql = 'select tagname from tagnames where tagname not in (select tagname from '
        sql += 'entitytags where entityid=%d)' % self.entityid
        self.app.db.cursor.execute(sql)
        rows = self.app.db.cursor.fetchall()
        tags = [row.tagname for row in rows]
        for tagname in tags:
            print 'adding', tagname, 'to list'
            KListViewItem(self.frame.listView, tagname)

        self.connect(self, SIGNAL('okClicked()'), self.add_tags)

    def add_tags(self):
        items = self.frame.listView.selectedItems()
        for item in items:
            tagname = str(item.text(0))
            self.app.db.tag(self.entityid, tagname)
            
        
class RemoveTagsDialog(BaseTagsDialog):
    def __init__(self, parent, entityid, name='RemoveTagsDialog'):
        BaseTagsDialog.__init__(self, parent, entityid, name=name)
        for tagname in self.app.db.get_tags(self.entityid):
            KListViewItem(self.frame.listView, tagname)
        self.connect(self, SIGNAL('okClicked()'), self.remove_tags)

    def remove_tags(self):
        items = self.frame.listView.selectedItems()
        for item in items:
            tagname = str(item.text(0))
            self.app.db.delete_tag(tagname, self.entityid)
            
            
class NewTagDialogOrig(BaseDialogWindow):
    def __init__(self, parent, name='NewTagDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.frame = QFrame(self)
        numrows = 2
        numcols = 1
        margin = 0
        space = 1
        self.grid = QGridLayout(self.frame, numrows, numcols,
                                margin, space, 'NewTagDialogLayout')
        self.lbl = QLabel('Enter new tag name', self.frame)
        self.entry = KLineEdit(self.frame, '')
        self.grid.addWidget(self.lbl, 0, 0)
        self.grid.addWidget(self.entry, 1, 0)

        self.setMainWidget(self.frame)
        
        self.connect(self, SIGNAL('okClicked()'),  self.create_new_tag)

    def create_new_tag(self):
        tagname = str(self.entry.text())
        self.app.db.create_tag(tagname)



########################
from useless.kdebase.dialogs import VboxDialog
class NewTagDialog(VboxDialog):
    def __init__(self, parent, name='NewTagDialog'):
        VboxDialog.__init__(self, parent, name=name)
        self.label = QLabel('Enter new tag name', self.frame)
        self.entry = KLineEdit(self.frame, '')
        self.vbox.setMargin(3)
        self.vbox.setSpacing(2)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.entry)
        self.connect(self, SIGNAL('okClicked()'), self.create_new_tag)

    def create_new_tag(self):
        tagname = str(self.entry.text())
        self.app.db.create_tag(tagname)
        
