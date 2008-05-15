import os

from xml.dom.minidom import Element, Text

class TooManyElementsError(StandardError):
    pass

# this class taken from useless.base.xmlfile
class ParserHelper(object):
    def _get_single_section(self, element, section):
        sections = element.getElementsByTagName(section)
        if len(sections) > 1:
            raise TooManyElementsError, 'too many %s sections' %section
        else:
            return sections

    def get_elements_from_section(self, element, section, tag, atts=[]):
        sections = self._get_single_section(element, section)
        if len(sections):
            return sections[0].getElementsByTagName(tag)
        else:
            return []

    def get_attribute(self, element, attribute):
        return element.getAttribute(attribute).encode()

    def get_single_element(self, element, tagname):
        elist = self._get_single_section(element, tagname)
        return elist[0]

    # eclass should be subclass of BaseTextElement
    # eclass should have single argument of textdata
    def get_text_element(self, eclass, tagname, element):
        txt_element = self.get_single_element(element, tagname)
        # pass an empty string to new_element
        new_element = eclass('')
        new_element.reform(txt_element)
        return new_element
        
# this class taken from useless.xmlgen.base
class BaseElement(Element):
    def __init__(self, tagname, **atts):
        Element.__init__(self, tagname)
        self.setAttributes(**atts)
        
    def setAttributes(self, **atts):
        for k,v in atts.items():
            if k == 'class_':
                self.setAttribute('class', str(v))
            else:
                self.setAttribute(k, str(v))

# this class modified from useless.base.xmlfile TextElement
class BaseTextElement(BaseElement):
    def __init__(self, name, text, **atts):
        BaseElement.__init__(self, name, **atts)
        self.set(text)

    def set(self, text):
        while self.hasChildNodes():
            del self.childNodes[0]
        if text is not None:
            textnode = Text()
            textnode.data = text
            self.appendChild(textnode)

    def get(self):
        if self.hasChildNodes():
            return self.firstChild.data.encode().strip()
        else:
            return ''

    # this method is used to "reform" a parsed element
    # so we can use get, set on the parsed element
    def reform(self, element):
        name = element.tagName.encode()
        if element.hasChildNodes():
            try:
                value = element.firstChild.data.encode()
            except AttributeError:
                value = None
        else:
            value = None
        atts = {}
        for att in dict(element.attributes):
            atts[att.encode()] = element.getAttribute(att).encode()
        BaseTextElement.__init__(self, name, value, **atts)

if __name__ == '__main__':
    pass
