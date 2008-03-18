import urlparse
import subprocess

from useless.base.path import path

from qt import QStringList
from qt import QUriDrag

from kdeui import KMessageBox

class Process(subprocess.Popen):
    pass

class BaseDropCatcher(object):
    def dragEnterEvent(self, event):
        event.accept(QUriDrag.canDecode(event))

    def _handle_drop_event(self, event):
        qlist = QStringList()
        if QUriDrag.decodeToUnicodeUris(event, qlist):
            return qlist
        
    def dropEvent(self, event):
        qlist = self._droplist(event)
        raise NotImplementedError, 'dropEvent not implemented in BaseDropCatcher'



class MainDropCatcher(BaseDropCatcher):
    def dropEvent(self, event):
        qlist = self._handle_drop_event(event)
        if qlist is not None:
            if len(qlist) == 1:
                url = str(qlist[0])
                try:
                    self.app.urlhandler.handle(url)
                except self.app.urlhandler.UnknownProtocolError:
                    KMessageBox.information(self, "Can't handle '%s' protocol")
                    
                
                
if __name__ == '__main__':
    du = Url('http://bard/dwww')
    u = Url('http://www.youtube.com/watch?v=R0VS_3XmEpY')
    f = Url('/freespace/home/umeboshi/Desktop/Lewis, C.S - The Chronicles of Narnia.pdf')
    bh = BaseUrlHandler()
    
