from qt import QWidget
from qt import PYSIGNAL, SIGNAL

from kdecore import KURL
from kdeui import KMessageBox


from useless.kdebase.htmlpart import BaseInfoPart

from base import MyUrl

from infodoc import InfoDoc

class RtorrentInfoPart(BaseInfoPart):
    def __init__(self, parent, name='RtorrentInfoPart'):
        BaseInfoPart.__init__(self, parent, name=name)
        self.clear_view()

    def set_info(self, infohash):
        self.clear_view()
        self.app.processEvents()
        self.begin()
        #self.doc.set_info(entityid)
        #self.entityid = entityid
        #self.write(self.doc.output())
        self.write(str(self.app.rtorrent.torrents[infohash]))
        self.end()
        #self.emit(PYSIGNAL('EntityInfoUpdated'), (entityid,))
        
    ####################################################
    # the methods in this section map url's to actions #
    ####################################################
    def urlSelected(self, url, button, state, target, args):
        print url
        return
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
            
    
