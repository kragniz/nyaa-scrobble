import urllib
import httplib
import re
import config
import os
import hashlib
import time

class Scrobbler(object):
    def __init__(self):
        self.token = self.getToken()

    def scrobble(self, artist, track, album=None):
        timestamp = str(int(time.time()))
        params = {'artist': artist,
                  'method': 'track.scrobble',
                  'track': track,
                  'timestamp': timestamp,
                  'api_key': config.apiKey,
                  'sk': self.sessionKey()}
        if album:
            params['album'] = album
        params['api_sig'] = self.sign(params)
        print self.request(params)

    def nowPlaying(self, artist, track, album=None):
        timestamp = str(int(time.time()))
        params = {'artist': artist,
                  'method': 'track.updateNowPlaying',
                  'track': track,
                  'timestamp': timestamp,
                  'api_key': config.apiKey,
                  'sk': self.sessionKey()}
        if album:
            params['album'] = album
 
        params['api_sig'] = self.sign(params)
        print self.request(params)

    def sessionKey(self):
        if os.path.exists(config.sessionFile):
            with open(config.sessionFile) as f:
                return f.read()
        else:
            self.logIn()
            return self.getSession()

    def request(self, args):
        params = urllib.urlencode(args)
        header = {'user-agent': 'musc/0.1',
                  'Content-type': 'application/x-www-form-urlencoded'}

        lastfm = httplib.HTTPConnection('ws.audioscrobbler.com')
        lastfm.request('POST', '/2.0/?' ,params, header)
        response = lastfm.getresponse()
        return response.read()

    def logIn(self):
        url = 'http://www.last.fm/api/auth/?api_key={0}&token={1}'.format(
                                                     config.apiKey,
                                                     self.token)
        print 'Please log in at this url then press enter:', url
        raw_input()

    def getSession(self):
        params = {'method': 'auth.getSession',
                  'api_key': config.apiKey,
                  'token': self.token}
        params['api_sig'] = self.sign(params)
        sessionKey = self.request(params)
        sessionKey = re.search('<key.+key>', sessionKey).group()[5:-6]
        with open(config.sessionFile, 'w') as f:
            f.write(sessionKey)
        return sessionKey

    def getToken(self):
        token = self.request({'method': 'auth.getToken',
                              'api_sig': config.apiSig,
                              'api_key': config.apiKey})
        return re.search('<token.+token>', token).group()[7:-8]

    def sign(self, methods):
        l = []
        s = ''
        for k, v in methods.items():
            l += [k+v]
        l.sort()
        for i in l:
            s += i
        return hashlib.md5(s+config.apiSig).hexdigest()


if __name__ == '__main__':
    s = Scrobbler()
    s.nowPlaying('Parov Stelar', 'For Rose')
