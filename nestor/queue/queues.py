"""
nestor.queue.queues
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from kombu import Exchange, Queue

# All queues should be prefixed with "nestor."
task_exchange = Exchange("tasks", type="direct")
task_queues = [
    Queue("nestor.default", task_exchange, routing_key="nestor.default"),
]
