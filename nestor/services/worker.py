"""
nestor.services.worker
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from nestor.services.base import Service


class NestorWorker(Service):
    name = 'worker'

    def run(self):
        import eventlet
        eventlet.patcher.monkey_patch()
        from nestor.queue.client import broker
        from nestor.queue.worker import Worker

        try:
            Worker(broker.connection).run()
        except KeyboardInterrupt:
            print("bye bye")
