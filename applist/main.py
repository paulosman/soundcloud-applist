import os
import urllib

import memcache

from flask import Flask, redirect, url_for, session, render_template, request

from applist.decorators import login_required
from applist.soundcloud import sc_request, get_access_token

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_envvar('APPLIST_SETTINGS')

mc = memcache.Client(app.config['MEMCACHED_SERVERS'])


@app.before_request
def initialize():
    token = mc.get('oauth_token')
    if app.debug and token:
        session['auth'] = token
        session.permanent = True


@app.route('/')
def index():
    if 'auth' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/app/<app_id>/')
def app_details(app_id):
    app_detail = sc_request(
        'apps/%s' % (app_id,), client_id=app.config['CLIENT_ID'])
    tracks = sc_request(
        'apps/%s/tracks' % (app_id,), client_id=app.config['CLIENT_ID'])
    return render_template(
        'app_details.html', tracks=tracks, details=app_detail)


@app.route('/dashboard/')
@login_required
def dashboard():
    app_url = request.args.get('app_url')
    if app_url:
        resolved = sc_request(
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

    data = get_access_token(
        app.config['CLIENT_ID'],
        app.config['CLIENT_SECRET'],
        url_for('callback', _external=True),
        'authorization_code',
        code
    )
    session['auth'] = data['access_token']
    session['scope'] = data['scope']
    session.permanent = True
    if app.debug:
        mc.set('oauth_token', data['access_token'])
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
