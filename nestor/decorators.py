"""
nestor.decorators
~~~~~~~~~~~~~~~~~
:copyright: (c) 2012 by FeedHQ (Bruno Renie).
:license: BSD, see LICENSE for more details.

Generic helpers for RQ task execution

Add to your settings:

RQ = {
'host': 'localhost',
'port': 6379,
'password': None,
'db': 0,
'charset': 'utf-8',
'errors': 'strict',
'unix_socket_path': None
'eager': False,
}

Everything's optional, these are just the default values.


"""
from functools import wraps

import redis
import rq

from django.conf import settings
from raven import Client


def enqueue(function, *args, **kwargs):
    opts = getattr(settings, 'RQ', {})
    eager = opts.pop('eager', False)
    if eager:
        return function(*args, **kwargs)
    else:
        conn = redis.Redis(**opts)
        queue = rq.Queue('nestor:default', connection=conn)
        return queue.enqueue(function, *args, **kwargs)


def raven(function):
    @wraps(function)
    def ravenify(*args, **kwargs):
        try:
            function(*args, **kwargs)
        except Exception:
            if not settings.DEBUG and hasattr(settings, 'SENTRY_DSN'):
                client = Client(dsn=settings.SENTRY_DSN)
                client.captureException()
            raise
    return ravenify
