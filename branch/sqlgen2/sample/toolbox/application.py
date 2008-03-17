import os
import traceback
from StringIO import StringIO

from qt import SIGNAL, SLOT, PYSIGNAL
from qt import QTimer

from kdecore import KAboutData
from kdecore import KApplication
from kdecore import KStandardDirs

from kdeui import KAboutDialog
from kdeui import KMessageBox

from dcopexport import DCOPExObj

from dblite import Connection, EntityManager
from urlhandler import MainUrlHandler

class ToolBoxDCOPInterface(DCOPExObj):
    def __init__(self, id='toolbox-handler'):
        DCOPExObj.__init__(self, id)
        
# about this program
class AboutData(KAboutData):
    def __init__(self):
        version = '0.0.0'
        KAboutData.__init__(self,
                            'toolbox',
                            'toolbox',
                            version,
                            "A Simple Custom Application")
        self.addAuthor('Joseph Rawson', 'author',
                       'umeboshi3@gmail.com')
        self.setCopyrightStatement('public domain')

class AboutDialog(KAboutDialog):
    def __init__(self):
        KAboutDialog.__init__(self, parent, *args)
        self.setTitle('Toolbox')
        self.setAuthor('Joseph Rawson')
        
# main application class
class MainApplication(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        # in case something needs done before quitting
        self.connect(self, SIGNAL('aboutToQuit()'), self.quit)
        self.dcop = ToolBoxDCOPInterface()
        self._setup_standard_directories()
        #self._generate_data_directories()
        dbfile = os.path.join(self.datadir, 'main.db')
        self.conn = Connection(dbname=dbfile, autocommit=True,
                               encoding='ascii')
        #self.guests = Guests(self.conn)
        self.db = EntityManager(self.conn)

        self.urlhandler = MainUrlHandler(self.db)
        # setup the timer to handle background jobs
        self.timer = QTimer()
        # every five seconds
        self.timer.changeInterval(1000)
        self.connect(self.timer, SIGNAL('timeout()'), self._timer_done)

        self.main_window = None
        
        
    # this method sets up the directories used by the application
    # with respect to the KDE environment
    # currently the main config file is placed in self.datadir
    # changes in the file dialogs used in the application will
    # be stored in the config file in its proper location
    # when I am ready to deal with changes to that config file
    # that my code doesn't use, I will probably move the main
    # config file to the regular config location
    def _setup_standard_directories(self):
        self._std_dirs = KStandardDirs()
        self.tmpdir_parent = str(self._std_dirs.findResourceDir('tmp', '/'))
        self.datadir_parent = str(self._std_dirs.findResourceDir('data', '/'))
        self.tmpdir = os.path.join(self.tmpdir_parent, 'toolbox')
        self.datadir = os.path.join(self.datadir_parent, 'toolbox')
        # we need this in dosbox object (for now)
        self.main_config_dir = self.datadir
        if not os.path.exists(self.datadir):
            os.mkdir(self.datadir)

    # This method is currently useless, but may be useful later
    # if some house cleaning needs doing before quitting
    def quit(self):
        # house cleaning chores go here
        KApplication.quit(self)

    def _timer_done(self):
        self.urlhandler.scan_jobs()
        if self.urlhandler.completed_jobs():
            self.urlhandler.handle_completed_jobs()
            self.emit(PYSIGNAL('UrlHandled'),(True,))
        jobs = self.urlhandler.jobs
        if jobs:
            self.main_window.label.setText('toolbox: %d jobs running' % len(jobs))
        else:
            self.main_window.label.setText('toolbox')
            
        
if __name__ == '__main__':
    print "testing module"
    
