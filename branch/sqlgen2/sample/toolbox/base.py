import urlparse



from useless.base.path import path

# we need these two imports for now
from useless.kdebase import get_application_pointer
from useless.kdebase.error import excepthook

class MyUrl(object):
    def __init__(self, delimiter='||'):
        self.delimiter = delimiter
    def make(self, *parts):
        return self.delimiter.join(parts)

    def parse(self, url):
        return url.split(self.delimiter)
    

if __name__ == '__main__':
    print "testing module"
    
    du = Url('http://bard/dwww')
    u = Url('http://www.youtube.com/watch?v=R0VS_3XmEpY')
    f = Url('/freespace/home/umeboshi/Desktop/Lewis, C.S - The Chronicles of Narnia.pdf')
