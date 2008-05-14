from sqlalchemy import sql
from sqlalchemy import Table, Column, ColumnDefault
from sqlalchemy.schema import MetaData, ForeignKey
from sqlalchemy.types import Integer, String, Text, Date

# metadata is the object that will be imported here
# it will contain all the schema defined below
metadata = MetaData()
# or instead of importing metadata in another module
# we define and map the objects in this one
from sqlalchemy.orm import mapper, relation
from sqlalchemy.orm.collections import column_mapped_collection

Name = String(50)
LongName = String(100)
BigName = String(255)


entity_fkey = 'entities.entityid'
etype_fkey = 'entity_types.type'
fieldname_fkey = 'entity_type_extfields.fieldname'
tagname_fkey = 'tagnames.tagname'

EntityTypeTable = Table('entity_types', metadata,
                        Column('type', Name, primary_key=True),
                        Column('desc', Text)
                        )

EntityTable = Table('entities', metadata,
                    Column('entityid', Integer, primary_key=True),
                    Column('type', None, ForeignKey(etype_fkey)),
                    Column('name', BigName),
                    Column('url', Text),
                    Column('desc', Text)
                    )

TagNameTable = Table('tagnames', metadata,
                     Column('tagname', BigName, primary_key=True)
                     )

EntityTagsTable = Table('entitytags', metadata,
                        Column('entityid', None, ForeignKey(entity_fkey),
                               primary_key=True),
                        Column('tagname', None, ForeignKey(tagname_fkey),
                               primary_key=True)
                        )

EntityTypeExtraFieldsTable = Table('entity_type_extfields', metadata,
                                   Column('type', None, ForeignKey(etype_fkey),
                                          primary_key=True),
                                   Column('fieldname', BigName, primary_key=True),
                                   Column('fieldtype', Name, ColumnDefault('name'))
                                   )
EntityExtraFieldsTable = Table('entity_extfields', metadata,
                               Column('entityid', None, ForeignKey(entity_fkey),
                                      primary_key=True),
                               Column('fieldname', None, ForeignKey(fieldname_fkey),
                                      primary_key=True),
                               Column('value', Text)
                               )


class BaseDbObject(object):
    def __repr__(self):
        pkeys = [k for k in self.c.keys() if self.c.get(k).primary_key]
        value = ', '.join([str(getattr(self, k)) for k in pkeys])
        return "<%s(%s)>" % (self.__class__.__name__, value)

class EntityType(BaseDbObject):
    def __init__(self, type, desc=None):
        self.type = type
        self.desc = desc
        

class Entity(BaseDbObject):
    pass

class EntityExtraField(BaseDbObject):
    pass

class ExtraField(BaseDbObject):
    def __init__(self, etype, fieldname, fieldtype='name'):
        self.type = etype
        self.fieldname = fieldname
        self.fieldtype = fieldtype
        


class Tag(BaseDbObject):
    def __init__(self, tagname):
        self.tagname = tagname
        


mapper(ExtraField, metadata.tables['entity_type_extfields'])
mapper(EntityType, metadata.tables['entity_types'],
       properties={
    'extfields' : relation(ExtraField)
    }
       )
mapper(Tag, metadata.tables['tagnames'])
mapper(EntityExtraField, metadata.tables['entity_extfields'])
mapper(Entity, metadata.tables['entities'],
       properties={
    'etype' : relation(EntityType),
    'tags': relation(Tag, secondary=metadata.tables['entitytags']),
    'extfields' : relation(EntityExtraField,
                           collection_class=column_mapped_collection(metadata.tables['entity_extfields'].c.fieldname))
    },
       allow_column_override=True
       )

#mapper(Guest, metadata.tables['guests'],
#       properties={
#    'works' : relation(Work, secondary=metadata.tables['guest_works']),
#    'appearances' : relation(Appearance),
#    'pictures' : relation(Picture, secondary=metadata.tables['guest_pictures'])
#    }
#       )

#mapper(Work, metadata.tables['all_works'])
#mapper(Appearance, metadata.tables['appearances'])
#mapper(Picture, metadata.tables['all_pictures'])

class EntityManager(object):
    ExtraField = ExtraField
    EntityExtraField = EntityExtraField
    EntityType = EntityType
    Tag = Tag
    Entity = Entity
    def __init__(self, session):
        self.session = session

    def _autocommit(self, obj):
        self.session.save_or_update(obj)
        if self.session.new or self.session.dirty:
            self.session.flush()
        
    def create_tag(self, tagname):
        tag = self.session.query(Tag).get(tagname)
        if tag is None:
            tag = Tag(tagname)
            self._autocommit(tag)
        return tag

    def create_entity_type(self, etype, desc=None):
        entity_type = self.session.query(EntityType).get(etype)
        if entity_type is None:
            entity_type = EntityType(etype, desc=desc)
            self._autocommit(entity_type)
        return entity_type

    def create_extra_field(self, etype, fieldname, fieldtype='name'):
        extfield = self.session.query(ExtraField).get((etype, fieldname))
        if extfield is None:
            extfield = ExtraField(etype, fieldname)
            self._autocommit(extfield)
        return extfield

    def get(self, entityid):
        return self.session.query(Entity).get(entityid)

    
    def tag(self, entity, tagname):
        if type(entity) is int:
            entity = self.get(entity)
        tag = self.create_tag(tagname)
        if tag not in entity.tags:
            entity.tags.append(tag)
        self._autocommit(entity)

    def untag(self, entity, tagname):
        tag = self.session.query(Tag).get(tagname)
        if tag is not None:
            del entity.tags[entity.tags.index(tag)]
        
    def get_entities(self, tags=[], etype=None):
        q = self.session.query(Entity)
        if tags:
            q = q.join('tags').filter(Tag.tagname.in_(tags))
        if etype:
            q = q.filter(Entity.type == etype)
        return q.all()
    
    
if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from useless.base.util import format_bytes

    engine = create_engine('sqlite:///test.db')
    transactional = False
    Session = sessionmaker(bind=engine, autoflush=True, transactional=transactional)
    
    session = Session()
    metadata.create_all(engine)
    em = EntityManager(session)
    
    

