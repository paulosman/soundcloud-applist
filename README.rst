=======
applist
=======

A simple project for playing around with the SoundCloud API.

Installation
------------

To install applist, `register your app with SoundCloud`_. Once you have a 
have a client id, create a file called ``settings.py`` and place it in the 
``applist`` directory. It should contain the following: ::

  CLIENT_ID = 'your soundcloud apps client id'
  MEMCACHED_SERVERS = ('127.0.0.1:11211',)

Now install the dependencies: ::

  pip install -r requirements.txt

Finally, run the application: ::

  APPLIST_SETTINGS=settings.py python run.py

.. _`register your app with SoundCloud`: http://soundcloud.com/you/apps/new
