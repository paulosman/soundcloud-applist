import urllib

import httplib2
import simplejson

URLS = {
    'BASE': 'https://api.soundcloud.com/%(path)s.%(fmt)s',
    'CONNECT': 'https://soundcloud.com/connect',
    'TOKEN': 'https://api.soundcloud.com/oauth2/token'
}


def _soundcloud_url(path, **kwargs):
    url = URLS['BASE'] % dict(path=path, fmt='json')
    if kwargs:
        url += '?%s' % (urllib.urlencode(kwargs),)
    return url


def sc_request(path, **kwargs):
    client = httplib2.Http()
    url = _soundcloud_url(path, **kwargs)
    resp, content = client.request(url)
    return simplejson.loads(content)


def get_access_token(client_id, client_secret, redirect_uri, grant_type, code):
    client = httplib2.Http()
    r, content = client.request(URLS['TOKEN'], 'POST', body=urllib.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': grant_type,
        'code': code,
    }))
    return simplejson.loads(content)
