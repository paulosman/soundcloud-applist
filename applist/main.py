import os

import memcache

from flask import Flask, redirect, url_for, render_template, request

from applist.soundcloud import sc_request

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_envvar('APPLIST_SETTINGS')

mc = memcache.Client(app.config['MEMCACHED_SERVERS'])


@app.route('/app/<app_id>/')
def app_details(app_id):
    app_detail = sc_request(
        'apps/%s' % (app_id,), client_id=app.config['CLIENT_ID'])
    tracks = sc_request(
        'apps/%s/tracks' % (app_id,), client_id=app.config['CLIENT_ID'])
    return render_template(
        'app_details.html', tracks=tracks, details=app_detail)


@app.route('/')
def index():
    app_url = request.args.get('app_url')
    if app_url:
        resolved = sc_request(
            'resolve', url=app_url, client_id=app.config['CLIENT_ID'])
        app_id = resolved['id']
        return redirect(url_for('app_details', app_id=app_id))
    return render_template('index.html')
