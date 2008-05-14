from qt import Qt, SIGNAL, SLOT, PYSIGNAL
from qt import QFrame
from qt import QLabel, QGridLayout

from kdeui import KLineEdit, KTextEdit
from kdeui import KListView, KListViewItem

from kdeui import KDialogBase
from kdeui import KPushButton
from kdeui import KStdGuiItem

from kdeui import KComboBox

from useless.kdebase import get_application_pointer
from useless.kdebase.dialogs import BaseDialogWindow
from useless.kdebase.dialogs import SimpleEntryDialog
from useless.kdebase.dialogs import VboxDialog


class AppFrame(QFrame):
    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.app = get_application_pointer()
    
class NewTagDialog(SimpleEntryDialog):
    def __init__(self, parent, name='NewTagDialog'):
        label = 'Enter a new tag name'
        SimpleEntryDialog.__init__(self, parent, label=label, name=name)

    def ok_clicked(self):
        tagname = str(self.entry.text())
        self.app.db.create_tag(tagname)

class SelectEntityTypeDialog(VboxDialog):
    def __init__(self, parent, name='SelectEntityTypeDialog'):
        VboxDialog.__init__(self, parent, name=name)
        self.label = QLabel('Select entity type', self.frame)
        self.combo = KComboBox(self.frame)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.combo)
        #etypes = self.app.db.get_entity_types()
        db = self.app.db
        etypes = [et.type for et in db.session.query(db.EntityType).all()]
        self.combo.insertStrList(etypes)
        self.connect(self.combo, SIGNAL('activated(const QString &)'),
                     self._etype_selected)
        
    def _etype_selected(self, etype):
        self.emit(SIGNAL('okClicked()'), tuple())
        self.close()
        
class BaseEntityDataFrame(AppFrame):
    def __init__(self, parent, name='BaseEntityDataFrame'):
        AppFrame.__init__(self, parent, name)
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
        self.etype_combo = KComboBox(self, 'etype_combo')
        db = self.app.db
        etypes = db.session.query(db.EntityType).all()
        self.etype_combo.insertStrList([e.type for e in etypes])
        self.connect(self.etype_combo, SIGNAL('activated(const QString &)'),
                                              self.change_etype)
        self.grid.addWidget(self.etype_lbl, 2, 0)
        self.grid.addWidget(self.etype_combo, 3, 0)

        self.url_lbl = QLabel('url', self)
        self.url_entry = KLineEdit('', self)

        self.grid.addWidget(self.url_lbl, 4, 0)
        self.grid.addWidget(self.url_entry, 5, 0)
        
        grid_rownum = 6
        
        
        self.desc_lbl = QLabel('Description', self)
        self.desc_entry = KTextEdit(self, 'description_entry')
        self.desc_entry.setTextFormat(self.PlainText)
        
        self.grid.addMultiCellWidget(self.desc_lbl, 6, 6, 0, 0)
        self.grid.addMultiCellWidget(self.desc_entry, 7, 10, 0, 0)

        #self.works_frame = BaseGuestWorksFrame(self)
        #self.grid.addMultiCellWidget(self.works_frame, 8, 8, 0, 1)


    def change_etype(self, etype):
        print 'change_etype', etype
        
    def get_data(self):
        name = str(self.name_entry.text())
        etype = str(self.etype_combo.currentText())
        url = str(self.url_entry.text())
        desc = str(self.desc_entry.text())
        data = dict(name=name, type=etype,
                    url=url, desc=desc)
        if self.entityid is not None:
            data['entityid'] = self.entityid
        return data

    def set_entity(self, entity):
        self.entity = entity
        self.set_data(entity)
        
    def set_data(self, entity):
        self.entityid = entity.entityid
        self.name_entry.setText(entity.name)
        self.etype_combo.setCurrentText(entity.type)
        self.url_entry.setText(entity.url)
        self.desc_entry.setText(entity.desc)
        
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
        updated = [(k, data[k]) for k in data.keys() if data[k] != getattr(self.entity, k)]
        if updated:
            for k, v in updated:
                setattr(self.entity, k, v)
            self.app.db.session.flush()
            
        
class MainEntityDialog(BaseEntityDialog):
    def __init__(self, parent, dtype='insert', entity=None, name='MainEntityDialog'):
        BaseEntityDialog.__init__(self, parent, name=name)
        self.entity = entity
        self._dtype = dtype
        if self._dtype == 'insert':
            self.connect(self, SIGNAL('okClicked()'), self.insert_entity)
        elif self._dtype == 'update':
            self.connect(self, SIGNAL('okClicked()'), self.update_entity)
            #data = self.app.db.get(self.entityid)
            data = dict([(k, getattr(self.entity, k)) for k in self.entity.c.keys()])
            self.set_data(entity)
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
    def __init__(self, parent, entity, name='BaseTagsDialog'):
        BaseDialogWindow.__init__(self, parent, name=name)
        self.entity = entity
        self.frame = BaseTagDialogFrame(self)
        self.setMainWidget(self.frame)
        self.frame.listView.setSelectionModeExt(KListView.Extended)
        
class AddTagsDialog(BaseTagsDialog):
    def __init__(self, parent, entity, name='AddTagsDialog'):
        BaseTagsDialog.__init__(self, parent, entity, name=name)
        sql = 'select tagname from tagnames where tagname not in (select tagname from '
        sql += 'entitytags where entityid=%d)' % self.entity.entityid
        db = self.app.db
        # we really should try and perform the sql above
        # or the sqlalchemy equivalent, but this will work
        # for now
        all_tags = db.session.query(db.Tag).all()
        tags = [tag.tagname for tag in all_tags if tag not in self.entity.tags]
        #self.app.db.cursor.execute(sql)
        #rows = self.app.db.cursor.fetchall()
        #tags = [row.tagname for row in rows]
        for tagname in tags:
            print 'adding', tagname, 'to list'
            KListViewItem(self.frame.listView, tagname)

        self.connect(self, SIGNAL('okClicked()'), self.add_tags)

    def add_tags(self):
        items = self.frame.listView.selectedItems()
        for item in items:
            tagname = str(item.text(0))
            self.app.db.tag(self.entity.entityid, tagname)
            
        
class RemoveTagsDialog(BaseTagsDialog):
    def __init__(self, parent, entity, name='RemoveTagsDialog'):
        BaseTagsDialog.__init__(self, parent, entity, name=name)
        for tag in entity.tags:
            KListViewItem(self.frame.listView, tag.tagname)
        self.connect(self, SIGNAL('okClicked()'), self.remove_tags)

    def remove_tags(self):
        items = self.frame.listView.selectedItems()
        for item in items:
            tagname = str(item.text(0))
            self.app.db.untag(self.entity, tagname)
            
            
            
