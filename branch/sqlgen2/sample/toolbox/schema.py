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

class EntityTable(Table):
    def __init__(self):
        idcol = AutoId('entityid')
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

class EntityTags(Table):
    def __init__(self):
        entityid = Num('entityid')
        tagname = Bigname('tagname')
        Table.__init__(self, 'entitytags', [entityid, tagname])

def generate_schema(cursor):
    tables = [EntityTable,
              TagNameTable,
              EntityTags]
    for table in tables:
        cursor.create_table(table())
        
    
    
if __name__ == '__main__':
    gt = GuestTable()
    
