import os
from httphandler import BaseHttpHandler
from sgmllib import SGMLParser
from sets import Set
import subprocess
import datetime

from useless.base.util import Url

class BaseParser(SGMLParser):
    def __init__(self, verbose=0):
        SGMLParser.__init__(self, verbose)
        self._data = ''
        self._write_data = False
        
    def handle_data(self, data):
        if self._write_data:
            self._data += data
            if not self.literal:
                self._write_data = False
        else:
            return SGMLParser.handle_data(self, data)
            
    def _clear_data(self):
        self._data = ''


class GalleryParser(BaseParser):
    def __init__(self, *args, **kw):
        BaseParser.__init__(self, *args, **kw)
        self._in_image_anchor = False
        self.image_urls = Set()
        
    def start_a(self, attributes):
        atts = dict(attributes)
        if self._in_image_anchor:
            raise RuntimeError, "can't handle anchors inside image anchors"
        
        if 'href' in atts and atts['href'].startswith('/wiki/Image:'):
            self._in_image_anchor = True
            #self.image_urls.append(atts['href'])
            self.image_urls.add(atts['href'])
            
    def end_a(self):
        if self._in_image_anchor:
            self._in_image_anchor = False
            
class ImagePageParser(BaseParser):
    def __init__(self, *args, **kw):
        BaseParser.__init__(self, *args, **kw)
        self._in_anchor = False
        
    def start_a(self, attributes):
        #print 'start_a', attributes
        self._in_anchor = True
        self._current_anchor = dict(attributes)
        
    def end_a(self):
        self._in_anchor = False
        
    def handle_data(self, data):
        if self._in_anchor:
            if data == "Full resolution":
                print data
                print self._current_anchor
                self.main_href = self._current_anchor['href']
                
                
class BaseImageHandler(BaseHttpHandler):
    def handle_main_page(self, url):
        self.main_url = Url(url)
        response = self.perform_request(url)
        data = response.read()
        self._handle_main_page_data(data)
        

    def _handle_main_page_data(self, data):
        parser = GalleryParser()
        parser.feed(data)
        self.image_wikipage_urls = []
        for image_path in parser.image_urls:
            url = Url(self.main_url)
            url.path = image_path
            url = Url(url)
            self.image_wikipage_urls.append(url)
        
    def get_fullres_image_urls(self):
        self.image_urls = Set()
        self.failed_urls = []
        for url in self.image_wikipage_urls:
            parser = self.handle_image_page(url)
            if not hasattr(parser, 'main_href'):
                self.failed_urls.append(Url(url))
            else:
                href = parser.main_href
                #self.image_urls.append(Url(href))
                self.image_urls.add(Url(href))
            
    def handle_image_page(self, url):
        response = self.perform_request(url)
        data = response.read()
        href = self._handle_image_page_data(data)
        return href
    
    def _handle_image_page_data(self, data):
        parser = ImagePageParser()
        parser.feed(data)
        return parser

    def write_file(self, filename):
        if self.image_urls:
            outfile = file(filename, 'w')
            for url in self.image_urls:
                outfile.write(url + '\n')
            outfile.close()
        else:
            raise RuntimeError, "Nothing to write"

    def _kget_section(self, index, url):
        section = 'Item%d\n' % index
        #section += 'Dest[$e]=file://%s\n' % path_to_here_and_filename
        here = os.getcwd()
        filename = os.path.basename(url)
        local_filename = os.path.join(here, filename)
        section += 'Dest[$e]=file://%s\n' % local_filename
        section += 'Mode=1\n'
        section += 'ProcessedSize=0\n'
        # add a day to keep it from going now
        stime = datetime.datetime.now() + datetime.timedelta(1)
        stime = ','.join([str(tp) for tp in stime.timetuple()[:6]])
        section += 'ScheduledTime=%s\n' % stime
        section += 'Source[$e]=%s\n' % url
        section += 'Status=2\n'
        section += 'TotalSize=0\n'
        return section
    
    def _get_kget_sections(self, urls):
        sections = []
        for index in range(len(urls)):
            section = self._kget_section(index, urls[index])
            sections.append(section)
        return sections
    
    def kget(self):
        cmd = ['kget'] + list(self.image_urls)
        subprocess.call(cmd)
        
    
    def get(self, url):
        self.handle_main_page(url)
        self.get_fullres_image_urls()
        self.kget()
        

if __name__ == '__main__':
    b = BaseImageHandler()
    url = 'http://en.wikipedia.org/wiki/User:Mbz1/Mbz1_gallery/Underwater'
    #r = b.perform_request(url)
    #data = file('testimagepage.html').read()
    #gp = GalleryParser()
    #gp.feed(data)
    #h = BaseImageHandler()
    #h.main_url = Url(url)
    #h._handle_main_page_data(data)
    #p = ImagePageParser()
    #p.feed(data)
    otherplaces = "http://en.wikipedia.org/wiki/User:Mbz1/Mbz1_gallery/Picture_Gallery_Other_places_I've_been_to"
    africa = "http://en.wikipedia.org/wiki/User:Mbz1/Mbz1_gallery/Africa"
    wildlife = "http://en.wikipedia.org/wiki/User:Mbz1/Mbz1_gallery/Picture_Gallery_Wildlife"
    fir002_featured = "http://en.wikipedia.org/wiki/User:Fir0002/Fir0002_gallery/Featured_Pictures"
    fir002_kodak = "http://en.wikipedia.org/wiki/User:Fir0002/Fir0002_gallery/kodak"
    fir002_canon = "http://en.wikipedia.org/wiki/User:Fir0002/Fir0002_gallery/canon"
    underwater = 'http://en.wikipedia.org/wiki/User:Mbz1/Mbz1_gallery/Underwater'
    hummingbird = 'http://en.wikipedia.org/wiki/User:Mbz1/Mbz1_gallery/Hummingbird'

    urls = dict(otherplaces=otherplaces, africa=africa, fir002_featured=fir002_featured,
                fir002_kodak=fir002_kodak, fir002_canon=fir002_canon, underwater=underwater,
                hummingbird=hummingbird)
    

    h = BaseImageHandler()
    #h.get(underwater)
    h.handle_main_page(underwater)
    sections = []
    for p in range(len(h.image_wikipage_urls)):
        sections.append(h._kget_section(p, h.image_wikipage_urls[p]))
        
    
