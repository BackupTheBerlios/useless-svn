import os
import traceback
import urlparse
import datetime

from StringIO import StringIO

from qt import SIGNAL, SLOT

from kdecore import KApplication

from kdeui import KMessageBox

def get_application_pointer():
    return KApplication.kApplication()


def excepthook(type, value, tracebackobj):
    separator = '-' * 80
    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: %s' % (str(type), str(value))
    sections = [separator, errmsg, separator]
    msg = '\n'.join(sections)
    KMessageBox.detailedError(None, msg, tbinfo)

class MyUrl(object):
    def __init__(self, delimiter='||'):
        self.delimiter = delimiter
    def make(self, *parts):
        return self.delimiter.join(parts)

    def parse(self, url):
        return url.split(self.delimiter)
    

if __name__ == '__main__':
    print "testing module"
    
