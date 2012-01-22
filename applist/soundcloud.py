import urllib
import hashlib

import requests
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


def _request(path, **kwargs):
    mc = g.mc
    response = mc.get(_request_key(path, **kwargs))
    if response:
        return response
    r = requests.get(_soundcloud_url(path, **kwargs))
    data = simplejson.loads(r.content)
    mc.set(_request_key(path, **kwargs), data)
    return data


def resolve_url(url):
    return _request('resolve', url=url,
                      client_id=g.app.config['CLIENT_ID'])


def get_app(app_id):
    return _request('apps/%s' % (app_id,),
                      client_id=g.app.config['CLIENT_ID'])


def get_tracks(app_id, order_by='created_at'):
    if order_by not in [None, 'created_at', 'hotness']:
        order_by = 'created_at'
    return _request(
        'apps/%s/tracks' % (app_id,), client_id=g.app.config['CLIENT_ID'],
        order=order_by)
