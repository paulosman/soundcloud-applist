import os
from urllib import quote, quote_plus

import memcache

from flask import Flask, redirect, url_for, render_template, request, g

from applist.soundcloud import sc_request, get_tracks

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_envvar('APPLIST_SETTINGS')

mc = memcache.Client(app.config['MEMCACHED_SERVERS'])


@app.before_request
def initialize():
    g.mc = mc
    g.app = app


@app.template_filter('urlencode')
def urlencode(uri, plus=True):
    return quote_plus(uri) if plus else quote(uri)


@app.route('/app/<app_id>/tracks/')
def app_tracks(app_id):
    order_by = request.args.get('order_by')
    return render_template('_tracks.html', tracks=get_tracks(
        app_id, order_by=order_by))


@app.route('/app/<app_id>/')
def app_details(app_id):
    order_by = request.args.get('order_by')
    app_detail = sc_request(
        'apps/%s' % (app_id,), client_id=app.config['CLIENT_ID'])
    tracks = get_tracks(app_id, order_by=order_by)
    return render_template(
        'app_details.html', tracks=tracks, app=app_detail)


@app.route('/')
def index():
    app_url = request.args.get('app_url')
    if app_url:
        resolved = sc_request(
            'resolve', url=app_url, client_id=app.config['CLIENT_ID'])
        app_id = resolved['id']
        return redirect(url_for('app_details', app_id=app_id))
    return render_template('index.html')
