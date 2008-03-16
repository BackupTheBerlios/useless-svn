import urlparse
import subprocess

from useless.base.path import path

from qt import QStringList
from qt import QUriDrag

class Process(subprocess.Popen):
    pass

class BaseDropCatcher(object):
    def dragEnterEvent(self, event):
        event.accept(QUriDrag.canDecode(event))

    def _droplist(self, event):
        qlist = QStringList()
        if QUriDrag.decodeToUnicodeUris(event, qlist):
            return qlist
        
    def dropEvent(self, event):
        qlist = self._droplist(event)
        raise NotImplementedError, 'dropEvent not implemented in BaseDropCatcher'



class MainDropCatcher(BaseDropCatcher):
    def dropEvent(self, event):
        qlist = self._droplist(event)
        if qlist is not None:
            if len(qlist) == 1:
                url = qlist[0]
                print type(url), url
                
class Url(object):
    def __init__(self, url):
        self.url_orig = url
        url = str(url)
        protocol, host, path_, parameters, query, frag_id = urlparse.urlparse(url)
        self.protocol = protocol
        self.host = host
        self.path = path(path_)
        self.parameters = parameters
        self.query = query
        self.frag_id = frag_id

    def astuple(self):
        return (self.protocol, self.host, self.path, self.parameters,
                self.query, self.frag_id)

    def asdict(self):
        return dict(protocol=self.protocol, host=self.host, path=self.path,
                    parameters=self.parameters, query=self.query, frag_id=self.frag_id)
    
    def output(self):
        return str(urlparse.urlunparse(self.astuple()))

    def __repr__(self):
        return 'Url -> %s' % self.output()

    def __str__(self):
        return self.output()

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
        self._protocol_handlers[url.protocol](url)

    def handle_file_protocol(self, url):
        print 'handle_file_protocol', url.path
        

    def handle_http_protocol(self, url):
        if url.host.endswith('youtube.com'):
            self.handle_youtube_url(url)

    def handle_youtube_url(self, url):
        print 'handle_youtube_url', url
        job = Process(('youtube-dl', '-g', '-2', str(url)), stdout=subprocess.PIPE)
        job.jobtype = 'youtube-dl'
        job.handled_url = url
        self.jobs.append(job)

    def handle_jobs(self):
        while self._complete_jobs:
            job = self._complete_jobs.pop(0)
            if job.jobtype == 'youtube-dl':
                title, flv_url, ignore = job.stdout.read().split('\n')
                self._handled_urls[job.handled_url] = dict(title=title, flv_url=flv_url,
                                                           jobtype=job.jobtype)
            else:
                raise ValueError, "unable to handle jobtype %s" % job.jobtype
            
        
    def handle_youtubedl_job(self, job):
        if job.returncode == 0:
            data = job.stdout.read()
            title, url, ignore = data.split('\n')
            return title, url
        else:
            raise OSError, 'job returned %d' % job.returncode


if __name__ == '__main__':
    du = Url('http://bard/dwww')
    u = Url('http://www.youtube.com/watch?v=R0VS_3XmEpY')
    f = Url('/freespace/home/umeboshi/Desktop/Lewis, C.S - The Chronicles of Narnia.pdf')
    bh = BaseUrlHandler()
    
