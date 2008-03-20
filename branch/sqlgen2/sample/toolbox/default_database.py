

# default entity types
etypes = ['person', 'wikipedia-article', 'youtube-video', 'website',
          'webpage', 'weblog']



extfields = {}
key = 'youtube-video'
for key in ['wikipedia-article', 'youtube-video', 'website',
            'webpage', 'weblog']:
    extfields[key] = [('main-url', 'url'), ('local-copy', 'bool'),
                      ('local-filename', 'text')]
extfields['youtube-video'].append(('youtubeid', 'name'))
extfields['person'] = [('firstname', 'name'), ('lastname', 'name')]

# manager is EntityManager
def initialize_database(manager):
    for etype in etypes:
        manager.create_entity_type(etype)
    for etype in extfields:
        for fieldname, fieldtype in extfields[etype]:
            print "create extra fieldname '%s' for etype '%s'" % (fieldname, etype)
            manager.create_extra_field(etype, fieldname, fieldtype=fieldtype)
            
    
    
