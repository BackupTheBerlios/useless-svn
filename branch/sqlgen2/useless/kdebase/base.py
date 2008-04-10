from qt import SIGNAL
from kdecore import KApplication

def get_application_pointer():
    return KApplication.kApplication()


class HasDialogs(object):
    def __init__(self):
        self.current_dialog = None

    def connect_dialog(self, window, ok_clicked):
        self.connect(window, SIGNAL('okClicked()'), ok_clicked)
        self.connect_destroy_dialog(window)
        
    def connect_destroy_dialog(self, window):
        self.connect(window, SIGNAL('cancelClicked()'), self.destroy_current_dialog)
        self.connect(window, SIGNAL('closeClicked()'), self.destroy_current_dialog)
        self.current_dialog = window

    def destroy_current_dialog(self):
        self.current_dialog = None
        
