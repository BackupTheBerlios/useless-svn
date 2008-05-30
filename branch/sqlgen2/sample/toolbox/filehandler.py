from qt import SIGNAL
from kdecore import KURL
from dcopext import DCOPObj
from kio import KIO

from useless.base.path import path
from useless.base.util import Url


class BaseFileHandler(object):
    # app is the KDE application
    def __init__(self, app):
        self.app = app
        # we need a config file for this
        # or a config table in the database
        self.main_path = path('~/toolbox').expand()
        if not self.main_path.exists():
            self.main_path.mkdir()
        self.jobs = {}

    def foobar(self):
        pass

    def _local_url(self, localpath):
        return Url('file://%s' % localpath)
    
    # download url to filename
    # use main download path
    def download(self, url, filename):
        dpath = self.main_path / 'downloads'
        if not dpath.exists():
            dpath.mkdir()
        url = Url(url)
        kl = KURL.List()
        kl.append(KURL(url))
        localpath = KURL(self._local_url(dpath / filename))
        
        job = KIO.copy(kl, localpath)
        job.jobtype = 'youtube-dl'
        job.connect(job, SIGNAL('result(KIO::Job *)'), self.job_done)
        job.filename = filename
        data = dict(url=url, jobtype='youtube-dl', filename=filename)
        job.mergeMetaData(data)
        
    def job_done(self, job):
        if not job.error():
            items = job.outgoingMetaData().items()
            data = dict([(str(k), str(v)) for k,v in items])
            filename = data['filename']
            print filename
            filename = self.main_path / 'downloads' / filename
        
        
