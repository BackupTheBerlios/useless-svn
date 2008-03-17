from useless.sqlgen.classes import Table, Column, ColumnType
from useless.sqlgen.defaults import Text, Name, Bigname
from useless.sqlgen.defaults import PkNum, Num, NUM
from useless.sqlgen.defaults import DateTime
from useless.sqlgen.defaults import PkBigname


DATE = ColumnType('date')
    
def Date(name):
    return Column(name, DATE)

class AutoId(Column):
    def __init__(self, colname):
        Column.__init__(self, colname, NUM)
        self.constraint.pk = True
        self.constraint.unique = True
        self.constraint.null = False
        self.constraint.auto = True

    def __write__(self):
        col = '%s' % self.name
        col += ' INTEGER AUTOINCREMENT'
        return col

class EntityTypeTable(Table):
    def __init__(self):
        etype = PkName('type')
        desc = Text('desc')
        Table.__init__(self, 'entity_types', [etype, desc])
        
class EntityTable(Table):
    def __init__(self):
        idcol = AutoId('entityid')
        # etype should be foreign key to EntityTypeTable
        etype = Name('type')
        name = Bigname('name')
        url = Text('url')
        desc = Text('desc')
        cols = [idcol, etype, name, url, desc]
        Table.__init__(self, 'entities', cols)

class TagNameTable(Table):
    def __init__(self):
        name = PkBigname('tagname')
        Table.__init__(self, 'tagnames', [name])

class EntityTagsTable(Table):
    def __init__(self):
        # entityid is foreign key to EntityTable
        entityid = PkNum('entityid')
        # tagname is foreign key to TagNameTable
        tagname = PkBigname('tagname')
        Table.__init__(self, 'entitytags', [entityid, tagname])

class ExtraFieldsTable(Table):
    def __init__(self):
        fieldname = PkBigname('fieldname')
        Table.__init__(self, 'extfields', [fieldname])

class EntityTypeExtraFieldsTable(Table):
    def __init__(self):
        # etype is foreign key to EntityTypeTable
        etype = PkName('type')
        # fieldname is foreign key to ExtraFieldsTable
        fieldname = PkBigname('fieldname')
        Table.__init__(self, 'entity_type_extfields', [etype, fieldname])
        
class EntityExtraFieldsTable(Table):
    def __init__(self):
        entityid = PkNum('entityid')
        fieldname = PkBigname('fieldname')
        value = Text('value')
        cols = [entityid, fieldname, value]
        Table.__init__(self, 'entity_extfields', cols)
        
def generate_schema(cursor):
    tables = [EntityTypeTable,
              EntityTable,
              TagNameTable,
              EntityTagsTable,
              ExtraFieldsTable,
              EntityTypeExtraFieldsTable,
              EntityExtraFieldsTable
              ]
    for table in tables:
        cursor.create_table(table())
        
    
    
if __name__ == '__main__':
    gt = GuestTable()
    
