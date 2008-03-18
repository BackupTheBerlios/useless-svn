

# default entity types
etypes = ['person', 'wikipedia-article', 'youtube-video']



extfields = {}
key = 'youtube-video'
extfields[key] = ['youtubeid']

# manager is EntityManager
def initialize_database(manager):
    for etype in etypes:
        manager.create_entity_type(etype)
    for etype in extfields:
        for fieldname in extfields[etype]:
            print "create extra fieldname '%s' for etype '%s'" % (fieldname, etype)
            manager.create_extra_field(etype, fieldname)
            
    
    
