from useless.kdebase.mainwin import BaseMainWindow

class BaseToolboxWindow(BaseMainWindow):
    def __init__(self, parent, name='BaseToolboxWindow'):
        BaseMainWindow.__init__(self, parent, name=name)
        self.main_toolbox_window = parent

    # the desired behavior of the application is to not
    # quit when the main window is hidden and the
    # current window is the last one being displayed
    #
    # normally closing the last visible window will
    # quit the application
    #
    # this ugly hack keeps this from happening
    def closeEvent(self, event):
        called_show = False
        if not self.main_toolbox_window.isVisible():
            self.main_toolbox_window.show()
            called_show = True
        name = str(self.name())
        BaseMainWindow.closeEvent(self, event)
        if called_show:
            self.main_toolbox_window.hide()
        del self.main_toolbox_window._child_windows[name]
        print self.main_toolbox_window._child_windows.keys()
        
            
