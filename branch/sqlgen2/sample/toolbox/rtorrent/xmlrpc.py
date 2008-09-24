import datetime

from xmlrpclib import ServerProxy, Error

class Server(ServerProxy):
    def __init__(self, url='http://localhost/RPC2'):
        ServerProxy.__init__(self, url)


class RemoteObject(object):
    """Base class for objects using xmlrpc server proxy"""
    def __init__(self, server):
        self.server = server


torrent_attributes = ['name', 'size_bytes',
                      'completed_bytes', 'message', 'directory', 'ratio',
                      'peer_exchange', 'peers_complete', 'peers_connected',
                      'peers_not_connected', 'priority', 'creation_date',
                      'complete', 'up_total', 'down_rate',
                      'up_rate']

class Torrent(RemoteObject):
    def __init__(self, server, infohash=None):
        RemoteObject.__init__(self, server)
        self.infohash = infohash
        self.name = '__unset__'
        self.attributes = ['infohash', 'name', 'size', 'chunk_size',
                           'num_chunks', 'directory', 'completed_bytes',
                           'message', 'ratio', 'peer_exchange', 'peers_connected',
                           'peers_not_connected', 'peers_complete', 'priority',
                           'creation_date']
        if self.infohash is not None:
            self.set_infohash(self.infohash)

    def __repr__(self):
        return 'Torrent(%s)' % self.name
    
    def set_infohash(self, infohash):
        self.infohash = infohash
        self.name = self.get_name()
        self.size = self.get_size_bytes()
        self.chunk_size = self.get_chunk_size()
        self.num_chunks = self.get_number_of_chunks()
        self.directory = self.get_directory()
        self.update_info()
        
    def update_info(self):
        self.completed_bytes = self.get_completed_bytes()
        self.message = self.get_message()
        self.ratio = self.get_ratio()
        self.peer_exchange = self.get_peer_exchange()
        self.peers_connected = self.get_peers_connected()
        self.peers_not_connected = self.get_peers_not_connected()
        self.peers_complete = self.get_peers_complete()
        self.priority = self.get_priority()
        self.creation_date = self.get_creation_date()

    def get_name(self):
        return self.server.d.get_name(self.infohash)

    def get_size_bytes(self):
        return self.server.d.get_size_bytes(self.infohash)

    def get_completed_bytes(self):
        return self.server.d.get_size_bytes(self.infohash)

    def get_message(self):
        return self.server.d.get_message(self.infohash)

    def get_directory(self):
        return self.server.d.get_message(self.infohash)

    def get_ratio(self):
        return self.server.d.get_ratio(self.infohash)

    def get_peer_exchange(self):
        return self.server.d.get_peer_exchange(self.infohash)

    def get_peers_complete(self):
        return self.server.d.get_peers_complete(self.infohash)

    def get_peers_connected(self):
        return self.server.d.get_peers_connected(self.infohash)

    def get_peers_not_connected(self):
        return self.server.d.get_peers_not_connected(self.infohash)

    def get_priority(self):
        return self.server.d.get_priority(self.infohash)

    def get_creation_date(self):
        timestamp = self.server.d.get_creation_date(self.infohash)
        return datetime.datetime.fromtimestamp(timestamp)
    
    def get_complete(self):
        return self.server.d.get_complete(self.infohash)

    def get_up_total(self):
        return self.server.d.get_up_total(self.infohash)

    def get_down_rate(self):
        return self.server.d.get_down_rate(self.infohash)

    def get_up_rate(self):
        return self.server.d.get_up_rate(self.infohash)
    
    def get_chunk_size(self):
        return self.server.d.get_chunk_size(self.infohash)

    def get_number_of_chunks(self):
        return self.server.d.get_size_chunks(self.infohash)
    
    def is_open(self):
        return self.server.d.is_open(self.infohash)

    def is_active(self):
        return self.server.d.is_active(self.infohash)

    def open(self):
        return self.server.d.open(self.infohash)

    def close(self):
        return self.server.d.close(self.infohash)

    def erase(self):
        return self.server.d.erase(self.infohash)
    
    
class Rtorrent(RemoteObject):
    def __init__(self, server):
        RemoteObject.__init__(self, server)
        self._update()
        

    def _update(self):
        hashlist = self.download_list()
        torrents = [Torrent(self.server, infohash) for infohash in hashlist]
        self.torrents = dict(zip(hashlist, torrents))
        self.torrent_list = torrents
        
        
    def download_list(self):
        return self.server.download_list()

        
if __name__ == "__main__":
    s = Server(url='http://roujin/RPC2')
    r = Rtorrent(s)
    import web
    import web
    def status_replace(status):
        return "unknown status"
    web.template.Template.globals['getattr'] = getattr
    render = web.template.render('templates/')
    t = r.torrent_list[3]
        
