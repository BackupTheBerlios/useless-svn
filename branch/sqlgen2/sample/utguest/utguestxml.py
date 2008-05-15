import base64

from xml.dom.minidom import Element, Text
from xml.dom.minidom import parse as parse_xml_file
from xml.dom.minidom import parseString as parse_xml_string

from useless.base.path import path

from basexml import ParserHelper
from basexml import BaseElement, BaseTextElement

class AppereanceElement(BaseElement):
    def __init__(self, date):
        BaseElement.__init__(self, 'appearance', date=str(date))

class AppereancesElement(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'appearances')

    def add_appearance(self, date):
        self.appendChild(AppereanceElement(date))
        
class DescriptionElement(BaseTextElement):
    def __init__(self, text):
        BaseTextElement.__init__(self, 'description', text)

class TitleElement(BaseTextElement):
    def __init__(self, text):
        BaseTextElement.__init__(self, 'title', text)

class Base64Element(BaseTextElement):
    def __init__(self, tagname, text='', **atts):
        BaseTextElement.__init__(self, tagname, text, **atts)

    def get(self):
        string = BaseTextElement.get(self)
        return base64.b64decode(string)

    def set(self, binary):
        string = base64.b64encode(binary)
        BaseTextElement.set(self, string)

class PictureElement(Base64Element):
    def __init__(self, filename, binary=''):
        Base64Element.__init__(self, 'picture', filename=filename)
        self.set(binary)
            

class PicturesElement(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'pictures')

    def add_picture(self, filename):
        filename = path(filename)
        self.appendChild(PictureElement(filename.basename(), filename.open().read()))
        
        
class DataElement(BaseElement):
    def __init__(self, tagname, **atts):
        BaseElement.__init__(self, tagname, **atts)
        self.title_element = TitleElement('')
        self.appendChild(self.title_element)
        self.desc_element = DescriptionElement('')
        self.appendChild(self.desc_element)
        
class WorkElement(DataElement):
    def __init__(self, url='', type='', title='', description=''):
        DataElement.__init__(self, 'work', url=url, type=type)
        if title:
            self.title_element.set(title)
        if description:
            self.desc_element.set(description)

class WorksElement(BaseElement):
    def __init__(self):
        BaseElement.__init__(self, 'works')

    def add_work(self, url='', type='', title='', description=''):
        self.appendChild(WorkElement(url=url, type=type, title=title,
                                     description=description))
        
    

class GuestElement(DataElement):
    def __init__(self, **attributes):
        DataElement.__init__(self, 'guest', **attributes)
        self.appearances = AppereancesElement()
        self.appendChild(self.appearances)
        self.works = WorksElement()
        self.appendChild(self.works)
        self.pictures = PicturesElement()
        self.appendChild(self.pictures)
        
        
        
class GuestElementParser(ParserHelper):
    def __init__(self):
        self.guest_element = None
        self.main_row = None
        self.appearances = None
        self.works = None
        
    def parse_file(self, xmlfile):
        parsed_xml = parse_xml_file(xmlfile)
        self.guest_element = self.get_single_element(parsed_xml, 'guest')
        # main guest data
        element = self.guest_element
        data = dict()
        for key in ['firstname', 'lastname', 'salutation']:
            data[key] = element.getAttribute(key).encode()
        data['title'] , data['description'] = self._get_title_and_desc(element)
        self.main_row = data
        
        # appearance data
        appearances_element = self.get_single_element(parsed_xml, 'appearances')
        appearances = []
        for  element in appearances_element.childNodes:
            appearances.append(element.getAttribute('date').encode())
        self.appearances_element = appearances_element
            
        # works data
        works_element = self.get_single_element(parsed_xml, 'works')
        works = []
        for element in works_element.childNodes:
            work = {}
            for att in ['url', 'type']:
                work[att] = element.getAttribute(att).encode()
            work['title'], work['description'] = self._get_title_and_desc(element)
            works.append(work)
        self.works_element = works_element
        
        # pictures data
        pictures_element = self.get_single_element(parsed_xml, 'pictures')
        pictures = []
        for element in pictures_element.childNodes:
            filename = element.getAttribute('filename').encode()
            data = element.firstChild.data.encode().strip()
            data = base64.b64decode(data)
            pictures.append(dict(filename=filename, data=data))
        self.pictures_element = pictures_element    
            
        self.appearances = appearances
        self.works = works
        self.pictures = pictures

        
            
            
    def _get_title_and_desc(self, element):
        title_element = TitleElement('')
        title_element.reform(element.childNodes[0])
        desc_element = DescriptionElement('')
        desc_element.reform(element.childNodes[1])
        return title_element.get(), desc_element.get()
            
if __name__ == '__main__':
    from StringIO import StringIO
    g = GuestElement()
    xmlfile = StringIO()
    xmlfile.write(g.toxml())
    xmlfile.seek(0)
    parsed = parse_xml_string(g.toxml())
    #gp = GuestElementParser(parsed)
    
    pe = PictureElement('foo.gz', file('foo.gz').read())
    
