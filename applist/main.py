import os
from urllib import quote, quote_plus

import memcache

from flask import Flask, redirect, url_for, render_template, request, g

from applist.soundcloud import get_app, get_tracks, resolve_url

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
def tracks(app_id):
    order_by = request.args.get('order_by')
    return render_template('_tracks.html', tracks=get_tracks(
        app_id, order_by=order_by))


@app.route('/app/<app_id>/')
def details(app_id):
    order_by = request.args.get('order_by')
    app_details = get_app(app_id)
    tracks = get_tracks(app_id, order_by=order_by)
    return render_template(
        'details.html', tracks=tracks, app=app_details)


@app.route('/')
def index():
    app_url = request.args.get('app_url')
    if app_url:
        resolved = resolve_url(app_url)
        if 'errors' in resolved:
            return render_template('index.html',
                                   error='Sorry, we couldn\'t find your app')
        app_id = resolved['id']
        return redirect(url_for('details', app_id=app_id))
    return render_template('index.html')
