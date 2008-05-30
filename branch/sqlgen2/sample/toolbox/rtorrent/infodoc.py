import os
import urlparse
import datetime

from genshi.builder import tag

from useless.xmlgen.forgenshi import BaseDocument
from useless.xmlgen.forgenshi import Table

#from base import MyUrl
#myurl = MyUrl()


class RtorrentDocument(BaseDocument):
    def set_torrent(self, torrent):
        self.setTitle(torrent.name)
        
    
if __name__ == '__main__':
    doc = RtorrentDocument('')
    
