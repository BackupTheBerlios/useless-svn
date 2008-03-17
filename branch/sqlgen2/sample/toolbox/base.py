import urlparse



from useless.base.path import path

# we need these two imports for now
from useless.kdebase import get_application_pointer
from useless.kdebase.error import excepthook

class Url(str):
    def __init__(self, url):
        str.__init__(self, str(url))
        self.url_orig = url
        url = str(url)
        protocol, host, path_, parameters, query, frag_id = urlparse.urlparse(url)
        self.protocol = protocol
        self.host = host
        self.path = path(path_)
        self.parameters = parameters
        self.query = query
        self.frag_id = frag_id

    def astuple(self):
        return (self.protocol, self.host, self.path, self.parameters,
                self.query, self.frag_id)

    def asdict(self):
        return dict(protocol=self.protocol, host=self.host, path=self.path,
                    parameters=self.parameters, query=self.query, frag_id=self.frag_id)
    
    def output(self):
        return str(urlparse.urlunparse(self.astuple()))

    def __repr__(self):
        return 'Url(%s)' % self.output()

    def __str__(self):
        return self.output()

    def __eq__(self, other):
        return other.__eq__(self.output())
    
    
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
