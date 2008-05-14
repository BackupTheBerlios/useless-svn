from qt import QWidget
from qt import PYSIGNAL, SIGNAL

from kdecore import KURL
from kdeui import KMessageBox

from useless.kdebase.htmlpart import BaseInfoPart

from base import get_application_pointer
from base import MyUrl

from infodoc import InfoDoc
#from dialogs import BaseEntityDialog
from dialogs import MainEntityDialog
from dialogs import BaseTagsDialog
from dialogs import AddTagsDialog
from dialogs import RemoveTagsDialog


myurl = MyUrl()

class InfoPart(BaseInfoPart):
    def __init__(self, parent, name='InfoPart'):
        BaseInfoPart.__init__(self, parent, name=name)
        self.doc = InfoDoc(self.app)


    def set_info(self, entity):
        self.clear_view()
        self.app.processEvents()
        self.begin()
        self.doc.set_info(entity)
        # don't know if we need this anymore
        # or if we need self.entity = entity
        # or maybe self.current_entity = entity
        self.entityid = entity.entityid
        self.current_entity = entity
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
        if ident != self.current_entity.entityid:
            msg = "ident != current_entity.entityid, %d, %d" \
                  % (ident, self.current_entity.entityid)
            raise RuntimeError, msg
        if action == 'edit':
            dlg = MainEntityDialog(self.dialog_parent,
                                   dtype='update', entity=self.current_entity)
            dlg.show()
                
        elif action == 'delete':
            print 'delete selected'

        elif action == 'addtag':
            dlg = AddTagsDialog(self.dialog_parent, self.current_entity)
            dlg.show()
        elif action == 'deltag':
            dlg = RemoveTagsDialog(self.dialog_parent, self.current_entity)
            dlg.show()
        else:
            KMessageBox.error(self.dialog_parent,
                              'Unknown action: %s' % action)
            
    
