import os

from useless.db.lowlevel import LocalConnection
from useless.db.midlevel import StatementCursor
from useless.sqlgen.clause import Eq

from schema import generate_schema


class EntityExistsError(StandardError):
    pass

class Connection(LocalConnection):
    def __init__(self, dbname='test.db', autocommit=1, encoding='utf-8'):
        LocalConnection.__init__(self, dbname=dbname, autocommit=autocommit,
                                 encoding=encoding)
        
    def stmtcursor(self):
        return StatementCursor(self)



class EntityManager(object):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.stmtcursor()
        if not self.cursor.tables():
            import schema, default_database
            schema.generate_schema(self.cursor)
            default_database.initialize_database(self)
            del schema
            del default_database
            
            
    def create_tag(self, tagname):
        self.cursor.insert(table='tagnames', data=dict(tagname=tagname))

    # redo this
    def create(self, name, etype='generic'):
        data = dict(name=name, type=etype)
        self.cursor.insert(table='entities', data=data)

    def create_entity_type(self, etype):
        self.cursor.insert(table='entity_types', data=dict(type=etype))

    def create_extra_field(self, etype, fieldname):
        data = dict(type=etype, fieldname=fieldname)
        self.cursor.insert(table='entity_type_extfields', data=data)

    def get_extra_fields(self, etype):
        clause = Eq('type', etype)
        rows = self.cursor.select(table='entity_type_extfields', clause=clause)
        return [row.fieldname for row in rows]
    
    def create_entity(self, data):
        name = data['name']
        clause = Eq('name', name)
        rows = self.cursor.select(fields=['name'], table='entities', clause=clause)
        if not rows:
            # this needs to be a default in sqlite
            if not data.has_key('type'):
                data['type'] = 'generic'
            efields = ['name', 'type', 'url', 'desc']
            edata = {}
            for field in efields:
                if data.has_key(field):
                    edata[field] = data[field]
            self.cursor.insert(table='entities', data=edata)
            entityid = self.get_id(edata['name'])
            etype = data['type']
            extfields = self.get_extra_fields(etype)
            print 'extfields', extfields, 'for etype', etype
            if extfields:
                extdata = dict(entityid=entityid)
                table = 'entity_extfields'
                for field in extfields:
                    extdata['fieldname'] = field
                    extdata['value'] = data[field]
                    self.cursor.insert(table=table, data=extdata)
        else:
            raise EntityExistsError, 'Entity %s already exists.' % name
        
    def tag(self, entityid, tagname):
        clause = Eq('tagname', tagname)
        rows = self.cursor.select(table='tagnames', clause=clause)
        if not rows:
            self.create_tag(tagname)
        data = dict(entityid=entityid, tagname=tagname)
        self.cursor.insert(table='entitytags', data=data)

    def get_entities(self, tags=[], etype=None):
        if tags:
            table = 'entities natural join entitytags'
        else:
            table = 'entities'
        clause = None
        if tags:
            clause = Eq('entitytags.tagname', tags[0])
            for tag in tags[1:]:
                clause = clause & Eq('entitytags.tagname', tag)
        if etype is not None:
            if tags:
                etclause = Eq('entities.type', etype)
            else:
                etclause = Eq('type', etype)
            if clause is None:
                clause = etclause
            else:
                clause = clause & etclause
        return self.cursor.select(table=table, clause=clause)

    def change_entity(self, entityid, data):
        clause = Eq('entityid', entityid)
        # make a copy
        data = dict(data.items())
        if data.has_key('entityid'):
            del data['entityid']
        self.cursor.update(table='entities', data=data, clause=clause)
        
    def change_type(self, entityid, etype):
        self.change_entity(entityid, dict(type=etype))
        
    def change_name(self, entityid, name):
        self.change_entity(entityid, dict(name=name))
        
    def get(self, entityid):
        clause = Eq('entityid', entityid)
        rows = self.cursor.select(table='entities', clause=clause)
        if len(rows) > 1:
            raise ValueError, 'too many rows'
        elif len(rows) == 1:
            return rows[0]
        else:
            return []
        
    
    
    def get_id(self, name, etype=None):
        clause = Eq('name', name)
        if etype is not None:
            clause = clause & Eq('type', etype)
        rows = self.cursor.select(table='entities', clause=clause)
        ids = [row.entityid for row in rows]
        if len(ids) == 1:
            return ids[0]
        elif len(ids) == 0:
            return None
        elif len(ids) > 1:
            if etype is None:
                return rows
            else:
                raise ValueError, 'too many rows for type %s' % etype
        else:
            raise IndexError, 'bad values, %s' % str(ids)
        
    def delete_tag(self, tagname, entityid=None):
        clause = Eq('tagname', tagname)
        if entityid is not None:
            clause = clause & Eq('entityid', entityid)
        self.cursor.delete(table='entitytags', clause=clause)
        if entityid is None:
            clause = Eq('tagname', tagname)
            self.cursor.delete(table='tagnames', clause=clause)
            
    def get_tags(self, entityid):
        clause = Eq('entityid', entityid)
        rows = self.cursor.select(table='entitytags', clause=clause, order=['tagname'])
        return [row.tagname for row in rows]

    def get_all_tags(self):
        rows = self.cursor.select(table='tagnames')
        return [row.tagname for row in rows]

    def extvalue_exists(self, fieldname, value):
        clause = Eq('fieldname', fieldname) & Eq('value', value)
        return len(self.cursor.select(table='entity_extfields', clause=clause))

    def get_entity_types(self):
        rows = self.cursor.select(table='entity_types')
        return [row.type for  row in rows]
    
        
    
if __name__ == '__main__':
    import os
    
    dbfile = 'test.db'
    if os.environ.has_key('DBFILE'):
        dbfile = os.environ['DBFILE']
    conn = Connection(dbname=dbfile,
                      autocommit=True, encoding='ascii')
    cursor = conn.stmtcursor()
    e = EntityManager(conn)
    
    clause = Eq('entitytags.tagname', 'US President')
    table = 'entities natural join entitytags'
    
