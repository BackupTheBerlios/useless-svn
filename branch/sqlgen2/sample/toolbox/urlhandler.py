import re
import urlparse
import subprocess

from useless.base.path import path

from base import Url
youtube_url_re = re.compile(r'^((?:http://)?(?:\w+\.)?youtube\.com/(?:v/|(?:watch(?:\.php)?)?\?(?:.+&)?v=))?([0-9A-Za-z_-]+)(?(1)[&/].*)?$')
                          
class Process(subprocess.Popen):
    pass

class UnhandledUrlError(ValueError):
    pass

# raise this error for urls that don't need
# to be handled anymore
class AlreadyHandledError(ValueError):
    pass

class UnknownProtocolError(KeyError):
    pass

class BaseProcessHandler(object):
    def __init__(self):
        self.jobs = []
        self._failed_jobs = []
        self._complete_jobs = []

    
    def _main_job_queue(self):
        if 'fake-job' in self.jobs:
            raise ValueError, 'fake-job is not supposed to be in jobs at beginning of queue run'
        self.jobs.append('fake-job')
        job = self.jobs.pop(0)
        while job != 'fake-job':
            if job.poll() is None:
                self.jobs.append(job)
            else:
                if job.returncode == 0:
                    self._complete_jobs.append(job)
                else:
                    self._failed_jobs.append(job)
            job = self.jobs.pop(0)
        if job != 'fake-job':
            raise ValueError, 'fake-job is supposed to be last job at end of queue run'
        
    def scan_jobs(self):
        self._main_job_queue()

    def new_job(self, job):
        self.jobs.append(job)
        
class BaseUrlHandler(BaseProcessHandler):
    def __init__(self):
        BaseProcessHandler.__init__(self)
        self._protocol_handlers = dict(http=self.handle_http_protocol,
                                       file=self.handle_file_protocol)
        self._handled_urls = {}
        
        
    def handle(self, url):
        url = Url(url)
        if url.protocol in self._protocol_handlers:
            self._protocol_handlers[url.protocol](url)
        else:
            raise UnknownProtocolError, 'Unknown protocol: %s' % url.protocol
        
    def handle_file_protocol(self, url):
        raise NotImplementedError, "don't call handle_file_protocol in base class"
            

    def handle_http_protocol(self, url):
        raise NotImplementedError, "don't call handle_http_protocol in base class"

    def completed_urls(self):
        return self._handled_urls.keys()

    def completed_jobs(self):
        return [job for job in self._complete_jobs]
    
    def retrieve_data(self, url):
        data = self._handled_urls[url]
        del self._handled_urls[url]
        return data
    
    def handle_job(self, job):
        raise NotImplementedError, "don't call handle_job in base class"

    def handle_completed_jobs(self):
        while self._complete_jobs:
            job = self._complete_jobs.pop(0)
            self.handle_job(job)


class MainUrlHandler(BaseUrlHandler):
    UnknownProtocolError = UnknownProtocolError
    def __init__(self, db):
        BaseUrlHandler.__init__(self)
        self.db = db
        
    def handle_http_protocol(self, url):
        if url.host.endswith('youtube.com'):
            match = youtube_url_re.match(url)
            if match is not None:
                self.handle_youtube_url(url)
            else:
                raise UnhandledUrlError, 'unable to handle url %s' % url
        else:
            raise UnhandledUrlError, 'unable to handle url %s' % url

        
    
    def handle_youtube_url(self, url):
        match = youtube_url_re.match(url)
        youtubeid = match.group(2)
        if not self.db.extvalue_exists('youtubeid', youtubeid):
            print 'handle_youtube_url', url
            job = Process(('youtube-dl', '-g', '-2', str(url)), stdout=subprocess.PIPE)
            job.jobtype = 'youtube-dl'
            job.handled_url = url
            job.youtubeid = youtubeid
            self.jobs.append(job)
        else:
            print "already have %s" % youtubeid
            
    def handle_job(self, job):
        if job.jobtype == 'youtube-dl':
            self.handle_youtubedl_job(job)
        else:
            raise ValueError, "unable to handle jobtype %s" % job.jobtype
            
        
    def handle_youtubedl_job(self, job):
        if job.returncode == 0:
            title, flv_url, ignore = job.stdout.read().split('\n')
            data = dict(title=title, flv_url=flv_url, jobtype=job.jobtype,
                        youtubeid=job.youtubeid)
            self._handled_urls[job.handled_url] = data            
        else:
            raise OSError, 'job returned %d' % job.returncode


if __name__ == '__main__':
    du = Url('http://bard/dwww')
    u = Url('http://www.youtube.com/watch?v=R0VS_3XmEpY')
    f = Url('/freespace/home/umeboshi/Desktop/Lewis, C.S - The Chronicles of Narnia.pdf')
    h = MainUrlHandler()
    y = youtube_url_re
    
