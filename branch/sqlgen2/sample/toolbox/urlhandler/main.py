import re
import urlparse
import subprocess
from subprocess import Popen as Process
from sqlalchemy.exceptions import InvalidRequestError

from useless.base.path import path
from useless.base.util import Url

from base import BaseUrlHandler


youtube_url_re = re.compile(r'^((?:http://)?(?:\w+\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?(?:.+&)?v=))?([0-9A-Za-z_-]+)(?(1)[&/].*)?$')
                          


class UnhandledUrlError(ValueError):
    pass

# raise this error for urls that don't need
# to be handled anymore
class AlreadyHandledError(ValueError):
    pass

class UnknownProtocolError(KeyError):
    pass


class MainUrlHandler(BaseUrlHandler):
    UnknownProtocolError = UnknownProtocolError
    def __init__(self, app):
        BaseUrlHandler.__init__(self)
        self.app = app
        self.db = self.app.db
        
    def handle_http_protocol(self, url):
        if url.host.endswith('youtube.com'):
            match = youtube_url_re.match(url)
            if match is not None:
                self.handle_youtube_url(url)
            else:
                raise UnhandledUrlError(url, 'unable to handle url %s' % url)
        else:
            raise UnhandledUrlError(url, 'unable to handle url %s' % url)

        
    def _do_youtube_job(self, youtubeid, url, entityid=None):
            print 'handle_youtube_url', url
            job = Process(('youtube-dl', '-g', '-2', str(url)), stdout=subprocess.PIPE)
            job.jobtype = 'youtube-dl'
            job.handled_url = url
            job.youtubeid = youtubeid
            job.entityid = entityid
            self.jobs.append(job)
            
    def handle_youtube_url(self, url):
        match = youtube_url_re.match(url)
        youtubeid = match.group(2)
        eef = self.db.EntityExtraField
        query = self.db.session.query(eef)
        extfield_query = query.filter(eef.fieldname == 'youtubeid').filter(eef.value == youtubeid)
        try:
            extfield = extfield_query.one()
        except InvalidRequestError, inst:
            # we expect this error
            if inst.message == 'No rows returned for one()':
                self._do_youtube_job(youtubeid, url)
                return 
            # but reraise others
            else:
                raise inst
        id_filter = query.filter(eef.entityid == extfield.entityid)
        lc_query = id_filter.filter(eef.fieldname == 'local-copy')
        lc = bool(int(lc_query.one().value))
        print "lc", lc
        if not lc:
            print "self._do_youtube_job"
            self._do_youtube_job(youtubeid, url, entityid=extfield.entityid)
            
            
            
    def handle_job(self, job):
        if job.jobtype == 'youtube-dl':
            self.handle_youtubedl_job(job)
        else:
            raise ValueError, "unable to handle jobtype %s" % job.jobtype
            
        
    def handle_youtubedl_job(self, job):
        if job.returncode == 0:
            title, flv_url, ignore = job.stdout.read().split('\n')
            data = dict(title=title, flv_url=flv_url, jobtype=job.jobtype,
                        youtubeid=job.youtubeid, entityid=job.entityid)
            self._handled_urls[job.handled_url] = data            
        else:
            raise OSError, 'job returned %d' % job.returncode


if __name__ == '__main__':
    du = Url('http://bard/dwww')
    u = Url('http://www.youtube.com/watch?v=R0VS_3XmEpY')
    f = Url('/freespace/home/umeboshi/Desktop/Lewis, C.S - The Chronicles of Narnia.pdf')
    h = MainUrlHandler()
    y = youtube_url_re
    
