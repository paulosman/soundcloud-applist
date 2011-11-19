import os
import urllib

import httplib2
import simplejson

from flask import Flask, redirect, url_for, session, render_template, request

from applist.decorators import login_required


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_envvar('APPLIST_SETTINGS')


def _soundcloud_url(path, **kwargs):
    url = 'https://api.soundcloud.com/%s.json' % (path,)
    if kwargs:
        url += '?%s' % (urllib.urlencode(kwargs),)
    return url


def soundcloud_request(path, **kwargs):
    client = httplib2.Http()
    url = _soundcloud_url(path, **kwargs)
    resp, content = client.request(url)
    return simplejson.loads(content)


@app.route('/')
def index():
    if 'auth' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/app/<app_id>/')
def app_details(app_id):
    app_detail = soundcloud_request(
        'apps/%s' % (app_id,), client_id=app.config['CLIENT_ID'])
    tracks = soundcloud_request(
        'apps/%s/tracks' % (app_id,), client_id=app.config['CLIENT_ID'])
    return render_template(
        'app_details.html', tracks=tracks, details=app_detail)


@app.route('/dashboard/')
@login_required
def dashboard():
    app_url = request.args.get('app_url')
    if app_url:
        resolved = soundcloud_request(
            'resolve', url=app_url, client_id=app.config['CLIENT_ID'])
        app_id = resolved['id']
        return redirect(url_for('app_details', app_id=app_id))
    return render_template('dashboard.html')


@app.route('/callback/')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error or not code:
        return redirect(url_for('index'))

    url = app.config['URLS']['TOKEN']
    client = httplib2.Http()
    resp, content = client.request(url, 'POST', body=urllib.urlencode({
        'client_id': app.config['CLIENT_ID'],
        'client_secret': app.config['CLIENT_SECRET'],
        'redirect_uri': url_for('callback', _external=True),
        'grant_type': 'authorization_code',
        'code': code,
    }))
    data = simplejson.loads(content)
    session['auth'] = data['access_token']
    session['scope'] = data['scope']
    session.permanent = True
    return redirect(url_for('index'))


@app.route('/login/')
def login():
    if 'auth' in session:
        return redirect(url_for('dashboard'))
    url = app.config['URLS']['CONNECT']
    return redirect('%s?%s' % (url, urllib.urlencode({
        'client_id': app.config['CLIENT_ID'],
        'response_type': 'code',
        'redirect_uri': url_for('callback', _external=True),
        'scope': 'non-expiring'
    })))
