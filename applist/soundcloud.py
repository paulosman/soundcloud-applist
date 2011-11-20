import urllib
import hashlib

import httplib2
import simplejson

from flask import g


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


def _request_key(path, **kwargs):
    unhashed = '%s:%s' % (path, simplejson.dumps(kwargs))
    return hashlib.md5(unhashed).hexdigest()


def sc_request(path, **kwargs):
    mc = g.mc
    response = mc.get(_request_key(path, **kwargs))
    if response:
        return response
    client = httplib2.Http()
    url = _soundcloud_url(path, **kwargs)
    resp, content = client.request(url)
    data = simplejson.loads(content)
    mc.set(_request_key(path, **kwargs), data)
    return data


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


def get_tracks(app_id, order_by='created_at'):
    if order_by not in [None, 'created_at', 'hotness']:
        order_by = 'created_at'
    return sc_request(
        'apps/%s/tracks' % (app_id,), client_id=g.app.config['CLIENT_ID'],
        order=order_by)
