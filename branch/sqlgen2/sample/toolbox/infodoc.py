import os
import urlparse
import datetime


from useless.base.forgethtml import SimpleDocument
from useless.base.forgethtml import Anchor, Table
from useless.base.forgethtml import TableRow, TableCell
from useless.base.forgethtml import TableHeader, Header
from useless.base.forgethtml import Image, Paragraph, Break
from useless.base.forgethtml import Inline, Ruler, Image, Span
from useless.base.forgethtml import Text

class Bold(Inline):
    tag = 'b'

from base import MyUrl

myurl = MyUrl()


class BaseMainTable(Table):
    def __init__(self, app, class_='BaseMainTable',
                 border=1, cellspacing=0, width='100%', **args):
        Table.__init__(self, class_=class_, border=border,
                       cellspacing=cellspacing, width=width)
        self.app = app
        
class BaseDocument(SimpleDocument):
    def __init__(self, app, tableclass=BaseMainTable,
                 title='BaseDocument', **args):
        SimpleDocument.__init__(self, title=title)
        self.app = app
        self.maintable = tableclass(self.app)
        self.body.set(self.maintable)


class MainTable(BaseMainTable):
    def __init__(self, app):
        BaseMainTable.__init__(self, app, class_='MainTable')
        self.app = app
        
    def set_info(self, entity):
        db = self.app.db
        self.entityid = entity.entityid
        #edata = db.get(entityid)
        #main = edata['main']
        #extras = edata['extras']
        #tags = edata['tags']

        # set name and main action links
        name = TableHeader(str(entity.name), colspan=2, align='center')
        name_row = TableRow(name)
        self.set(name_row)
        edit_anchor = Anchor('(edit)',
                             href=myurl.make('edit', 'entity', str(entity.entityid)))
        delete_anchor = Anchor('(delete)',
                               href=myurl.make('delete', 'entity', str(entity.entityid)))
        cell = TableCell(edit_anchor)
        self.append(TableRow(cell))
        cell = TableCell(delete_anchor)
        self.append(TableRow(cell))

        
        # set type
        cell = TableCell('type:  %s' % str(entity.type), colspan=2)
        self.append(TableRow(cell))
        
        # extra fields
        if entity.extfields:
            self.append(TableRow(TableCell(Bold('Extra Fields'))))
            for field in entity.extfields:
                label = str('%s:  %s' % (field, str(entity.extfields[field].value)))
                cell = TableCell(label)
                self.append(TableRow(cell))

        # back to main data
        if entity.url:
            urlanchor = Anchor('url', href=str(entity.url))
            self.append(TableRow(TableCell(urlanchor, colspan=2)))
        if entity.desc:
            self.append(TableRow(TableCell(Bold('Description'), colspan=2)))
            desc = Paragraph(str(entity.desc))
            cell = TableCell(desc)
            self.append(TableRow(cell, colspan=2))

        # handle tags
        tagrow = TableRow()
        tagrow.append(TableCell(Bold('Tags'), colspan=2))
        span = Span(style='font-size: xx-small')
        add_anchor = Anchor('(add)',
                            href=myurl.make('addtag', 'entity', str(entity.entityid)))
        del_anchor = Anchor('(remove)',
                            href=myurl.make('deltag', 'entity', str(entity.entityid)))
        span.set(add_anchor)
        span.append(del_anchor)
        cell = TableCell(span, colspan=2)
        tagrow.append(cell)
        self.append(tagrow)
        for tag in entity.tags:
            row = TableRow()
            cell = TableCell(str(tag.tagname))
            row.set(cell)
            self.append(row)
        
class InfoDoc(BaseDocument):
    def __init__(self, app, tableclass=MainTable,
                 title='Information', **args):
        BaseDocument.__init__(self, app, tableclass=tableclass,
                              title=title, **args)

    def set_info(self, entityid):
        self.maintable.set_info(entityid)
        
