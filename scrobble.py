import urllib
import httplib
import re
import os
import hashlib
import time

class Scrobbler(object):
    def __init__(self, key, secret, sessionFile='.nyaa'):
        self.key = key
        self.secret = secret
        self.token = self.get_token()
        self.sessionFile = sessionFile

    def scrobble(self, artist, track, album=None):
        timestamp = str(int(time.time()))
        params = {'artist': artist,
                  'method': 'track.scrobble',
                  'track': track,
                  'timestamp': timestamp,
                  'api_key': self.key,
                  'sk': self.session_key()}
        if album:
            params['album'] = album
        params['api_sig'] = self.sign(params)
        print self.request(params)

    def now_playing(self, artist, track, album=None):
        timestamp = str(int(time.time()))
        params = {'artist': artist,
                  'method': 'track.updateNowPlaying',
                  'track': track,
                  'timestamp': timestamp,
                  'api_key': self.key,
                  'sk': self.session_key()}
        if album:
            params['album'] = album
 
        params['api_sig'] = self.sign(params)
        print self.request(params)

    def session_key(self):
        if os.path.exists(self.sessionFile):
            with open(self.sessionFile) as f:
                return f.read()
        else:
            self.log_in()
            return self.get_session()

    def request(self, args):
        params = urllib.urlencode(args)
        header = {'user-agent': 'nyaa-scrobble/0.1',
                  'Content-type': 'application/x-www-form-urlencoded'}

        lastfm = httplib.HTTPConnection('ws.audioscrobbler.com')
        lastfm.request('POST', '/2.0/?' ,params, header)
        response = lastfm.getresponse()
        return response.read()

    def log_in(self):
        url = 'http://www.last.fm/api/auth/?api_key={0}&token={1}'.format(
                                                     self.key,
                                                     self.token)
        print 'Please log in at this url then press enter:', url
        raw_input()

    def get_session(self):
        params = {'method': 'auth.getSession',
                  'api_key': self.key,
                  'token': self.token}
        params['api_sig'] = self.sign(params)
        sessionKey = self.request(params)
        sessionKey = re.search('<key.+key>', sessionKey).group()[5:-6]
        with open(self.sessionFile, 'w') as f:
            f.write(sessionKey)
        return sessionKey

    def get_token(self):
        token = self.request({'method': 'auth.getToken',
                              'api_sig': self.secret,
                              'api_key': self.key})
        return re.search('<token.+token>', token).group()[7:-8]

    def sign(self, methods):
        l = []
        s = ''
        for k, v in methods.items():
            l += [k+v]
        l.sort()
        for i in l:
            s += i
        return hashlib.md5(s+self.secret).hexdigest()


if __name__ == '__main__':
    s = Scrobbler()
    s.now_playing('Parov Stelar', 'For Rose')
