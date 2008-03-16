from qt import QWidget
from qt import PYSIGNAL, SIGNAL

#from kdecore import KURL
from kdeui import KMessageBox
from khtml import KHTMLPart
#from kfile import KFileDialog
#from dcopext import DCOPObj
#from kio import KIO

#from useless.base.util import md5sum

from base import get_application_pointer
from base import MyUrl

from infodoc import InfoDoc
#from dialogs import BaseEntityDialog
from dialogs import MainEntityDialog
from dialogs import BaseTagsDialog
from dialogs import AddTagsDialog
from dialogs import RemoveTagsDialog


myurl = MyUrl()

class InfoPart(KHTMLPart):
    def __init__(self, parent, name='InfoPart'):
        KHTMLPart.__init__(self, parent, name)
        self.app = get_application_pointer()
        self.dialog_parent = QWidget(None, 'dialog_parent')
        self.doc = InfoDoc(self.app)
        self.blank_window()

        # dialog markers
        self._update_entity_dlg = None
        
    def blank_window(self):
        self.begin()
        self.write('')
        self.end()

    def set_info(self, entityid):
        self.blank_window()
        self.app.processEvents()
        self.begin()
        self.doc.set_info(entityid)
        self.entityid = entityid
        self.write(self.doc.output())
        self.end()
        #self.emit(PYSIGNAL('EntityInfoUpdated'), (entityid,))
        
    ####################################################
    # the methods in this section map url's to actions #
    ####################################################
    def urlSelected(self, url, button, state, target, args):
        if url.find('||') > -1:
            self._perform_url_action(url)
        else:
            self.openURL(KURL(url))

    def _perform_url_action(self, url):
        parsed = myurl.parse(str(url))
        print parsed
        action, atype, ident = parsed
        if ident.isdigit():
            ident = int(ident)
        if action == 'edit':
            if self._update_entity_dlg is None:
                dlg = MainEntityDialog(self.dialog_parent, dtype='update', entityid=ident)
                dlg.show()
                
        elif action == 'delete':
            print 'delete selected'

        elif action == 'addtag':
            dlg = AddTagsDialog(self.dialog_parent, ident)
            dlg.show()
        elif action == 'deltag':
            dlg = RemoveTagsDialog(self.dialog_parent, ident)
            dlg.show()
        else:
            KMessageBox.error(self.dialog_parent,
                              'Unknown action: %s' % action)
            
    
