import os
import urllib2

from useless.base.path import path

class BaseHttpHandler(object):
    UserAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    Charset = 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    Mimes = 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
    Language = 'en-us,en;q=0.5'

    def __init__(self):
        self.cookies = urllib2.HTTPCookieProcessor()
        self.proxy = urllib2.ProxyHandler()
        self._install_handlers()

    def _install_handlers(self):
        install = urllib2.install_opener
        build = urllib2.build_opener
        install(build(self.proxy))
        install(build(self.cookies))

    # taken from youtube-dl
    def make_request(self, url, data=None):
        request = urllib2.Request(url)
        if data is not None:
            request.add_data(data)
        request.add_header('User-Agent', self.UserAgent)
        request.add_header('Accept-Charset', self.Charset)
        request.add_header('Accept', self.Mimes)
        request.add_header('Accept-Language', self.Language)
        return request

    def perform_request(self, url, data=None):
        request = self.make_request(url, data=data)
        response = urllib2.urlopen(request)
        return response
    
        
if __name__ == '__main__':
    h = BaseHttpHandler()
