"""
nestor.management.commands.retry_deferred
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import logging

from django.core.management.base import NoArgsCommand

from nestor.models import WufooRequest


class Command(NoArgsCommand):
    help = "Attempt to deploy any deferred request."

    def handle_noargs(self, **options):
        log_levels = {
            '0': logging.WARNING,
            '1': logging.INFO,
            '2': logging.DEBUG,
        }
        level = log_levels[options['verbosity']]
        logging.basicConfig(level=level, format="%(message)s")
        count = WufooRequest.objects.retry_deferred()
        logging.info("%s request(s) retried" % count)
