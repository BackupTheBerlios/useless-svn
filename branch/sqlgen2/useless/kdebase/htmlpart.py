from qt import QWidget

from khtml import KHTMLPart

from base import get_application_pointer
from base import HasDialogs

class BaseInfoPart(KHTMLPart, HasDialogs):
    def __init__(self, parent, name='BaseInfoPart'):
        KHTMLPart.__init__(self, parent, name)
        HasDialogs.__init__(self)
        self.app = get_application_pointer()
        self.dialog_parent = QWidget(self.parent(), 'dialog_parent')

    def _clearit(self):
        self.begin()
        self.write('')
        self.end()

    
    # this protected slot should be implemented in a subclass
    # it does nothing by default
    def urlSelected(self, url, button, state, target, args):
        pass

    
    
