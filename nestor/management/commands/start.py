"""
nestor.management.commands.start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from optparse import make_option


class Command(BaseCommand):
    args = '<service>'
    help = 'Starts the specified service'

    option_list = BaseCommand.option_list + (
        make_option('--debug',
            action='store_true',
            dest='debug',
            default=False),
    )

    def handle(self, service_name='http', **options):
        from nestor.services import worker

        services = {
            'worker': worker.NestorWorker,
        }

        # Ensure we perform an upgrade before starting any service
        print "Performing upgrade before service startup..."
        call_command('upgrade', verbosity=0)

        try:
            service_class = services[service_name]
        except KeyError:
            raise CommandError('%r is not a valid service' % service_name)

        service = service_class(
            debug=options['debug'],
        )

        print "Running service: %r" % service_name
        service.run()
