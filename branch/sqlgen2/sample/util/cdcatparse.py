from gzip import GzipFile
from xml.dom.minidom import parseString as parse_string
from xml.dom.minidom import parse as parse_file

import xml.parsers.expat

from useless.base.path import path

class Stack(list):
    def push(self, item):
        return list.append(self, item)

    def pop(self):
        return list.pop(self)

    def top(self):
        return self[-1]
    
    

class HCFSplitter(object):
    def __init__(self, filename):
        self.set_file(filename)
        self.current_path = path.getcwd()
        self.dirstack = Stack()
        self.set_parser()
        self._start_methods = dict(catalog=self.start_catalog,
                                   media=self.start_media,
                                   directory=self.start_directory,
                                   file=self.start_file)
        self._end_methods = dict(catalog=self.end_catalog,
                                 media=self.end_media,
                                 directory=self.end_directory)
        
    def set_parser(self):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.parser.CharacterDataHandler = self.char_data

    def set_file(self, filename=None):
        if filename is not None:
            self.filename = path(filename)
        if hasattr(self, '_file'):
            self._file.close()
        self._file = GzipFile(self.filename)
        # we need a new parser for a new file
        # using the old parser will cause errors
        # and eventually segfault
        self.set_parser()
        
    def start_element(self, name, attrs):
        if name in self._start_methods:
            self._start_methods[name](attrs)
        

    def end_element(self, name):
        if name in self._end_methods:
            self._end_methods[name]()

    def char_data(self, data):
        pass

    def Parse(self):
        self.parser.Parse(self._file.read())

    def start_catalog(self, attrs):
        self._current_catalog = attrs['name']
        print "starting catalog", self._current_catalog
        self.current_path = self.current_path / self._current_catalog
        self.current_path.mkdir()
        
    def end_catalog(self):
        print 'ending catalog', self._current_catalog
        print

    def start_media(self, attrs):
        self._current_media = attrs['name']
        print "starting media", self._current_media
        self.current_path  = self.current_path / self._current_media
        self.current_path.mkdir()
        
    def end_media(self):
        print 'ending media', self._current_media
        print self.current_path
        self.current_path = self.current_path.dirname()
        print

    def start_directory(self, attrs):
        dirname = attrs['name']
        #print 'starting directory', dirname
        self.dirstack.push(dirname)
        self.current_path = self.current_path / dirname
        self.current_path.mkdir()
        
        
    def end_directory(self):
        print 'ending directory', self.dirstack.top()
        self.dirstack.pop()
        self.current_path = self.current_path.dirname()
        print self.current_path
        
    def start_file(self, attrs):
        filename = attrs['name']
        file(self.current_path / filename, 'w')
        
if __name__ == '__main__':
    roname = 'ro-media-catalog.hcf'
    ro = GzipFile(roname)
    #data = ro.read()
    #p = parse_file(ro)
    here = path.getcwd()
    #ph = HCFParser(roname)
    p = HCFSplitter(roname)
    
