"""
nestor.queue.client
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django.conf import settings
from nestor.queue.queues import task_queues, task_exchange


from kombu import BrokerConnection
from kombu.common import maybe_declare
from kombu.pools import producers


class Broker(object):
    def __init__(self, broker_url):
        self.broker_url = broker_url

    def _get_connection(self):
        if hasattr(self, '_connection'):
            return self._connection

        self._connection = BrokerConnection(self.broker_url)

        with producers[self.connection].acquire(block=False) as producer:
            for queue in task_queues:
                maybe_declare(queue, producer.channel)

        return self._connection

    connection = property(_get_connection)

    def delay(self, func, *args, **kwargs):
        payload = {
            "func": func,
            "args": args,
            "kwargs": kwargs,
        }

        with producers[self.connection].acquire(block=False) as producer:
            producer.publish(payload,
                exchange=task_exchange,
                serializer="pickle",
                compression="bzip2",
                queue='nestor.default',
                routing_key='nestor.default',
            )


class EagerBroker(Broker):
    """
    Executes tasks within the same process.
    """
    def delay(self, func, *args, **kwargs):
        return func(*args, **kwargs)

if not settings.USE_QUEUE:
    broker = EagerBroker(settings.BROKER_URL)
else:
    broker = Broker(settings.BROKER_URL)
delay = broker.delay
