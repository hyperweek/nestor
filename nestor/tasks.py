"""
nestor.commands
~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import logging

from django.conf import settings
from django.db import connection
from django.db import transaction

from .decorators import enqueue, raven

logger = logging.getLogger('nestor')


@raven
def setup_and_deploy(request, **kwargs):
    from django.db.models import Count
    from django.core.mail import mail_admins

    from dploi_server.models import (Application, Deployment, UserInstance,
        Gunicorn, GunicornInstance)

    instance_type = kwargs.get('instance_type', 'trial')
    HOST_INSTANCES = getattr(settings, 'HOST_INSTANCES', 20)
    NOTIFICATION_THRESHOLD = getattr(settings, 'NOTIFICATION_THRESHOLD', 15)

    hosts = Gunicorn.objects.filter(is_enabled=True)\
        .annotate(num_instances=Count('instances'))\
        .exclude(num_instances__gte=HOST_INSTANCES)\
        .order_by('-num_instances')

    if not hosts:
        request.defer()
        logger.error('No host available for request #%s' % request.pk)

    target = hosts[0]
    used_slots = target.instances.count()
    if used_slots >= NOTIFICATION_THRESHOLD:
        available_slots = HOST_INSTANCES - used_slots
        host = target.host
        mail_admins(subject='nestor alert -- Server capacity almost full %s' % host.hostname,
            message="""Server capacity almost full %s

Action: alert
Host: %s
Description: only %d remaning slots available

Please, take any action to prevent overload capacity.

Your faithful employee,
nestor
""" % (host.hostname, host.public_ipv4, available_slots))

    with transaction.commit_on_success():
        application = Application()
        application.name = request.network_name
        application.verbose_name = request.company
        application.save()

        deployment = Deployment()
        deployment.application = application
        deployment.is_live = True
        deployment.name = instance_type
        deployment.save()

        user = UserInstance()
        user.deployment = deployment
        user.username = request.username
        user.email = request.email
        user.first_name = request.first_name
        user.last_name = request.last_name
        user.save()

        instance = GunicornInstance()
        instance.service = target
        instance.deployment = deployment
        instance.workers = 1
        instance.save()

    if settings.USE_DNSSIMPLE:
        enqueue(setup_dns, deployment)

    enqueue(deploy, deployment)
    request.delete()


@raven
def setup_dns(deployment, **kwargs):
    from dnsimple.api import DNSimple

    host = deployment.gunicorn_instances.get().service.host
    app = deployment.application

    base_domain = host.realm.base_domain

    dns = DNSimple(settings.DNSIMPLE_USER, settings.DNSIMPLE_PASSWORD)
    domain = dns.domains[base_domain]
    domain.add_record(app.name, 'ALIAS', host.hostname)


@raven
def deploy(deployment, **kwargs):
    """
    Deploy an application to a remote machine.

    First, it generates a puppet manifest, then connect to the
    remote machine and call puppet apply with the generated manifest
    as parameter.
    """
    from fabric.api import env, sudo
    from fabric.contrib.files import upload_template
    from fabric.network import disconnect_all

    try:
        host = deployment.gunicorn_instances.get().service.host
        app = deployment.application
        domain = '%s.%s' % (app.name, host.realm.base_domain)
        app_user = deployment.user_instances.get()

        SSH_PORT = getattr(settings, 'SSH_PORT', 22)
        SSH_USER = getattr(settings, 'SSH_USER', 'ubuntu')
        SSH_PASSWORD = getattr(settings, 'SSH_PASSWORD', None)
        SSH_KEYFILE = getattr(settings, 'SSH_KEYFILE', None)

        env.host_string = '%s@%s:%s' % (SSH_USER, host.private_ipv4, SSH_PORT)
        env.user = SSH_USER
        env.password = SSH_PASSWORD
        env.key_filename = SSH_KEYFILE
        env.timeout = 60 * 10

        context = {
            'user': env.user,
            'group': env.user,
            'app_name': app.name,
            'app_domain': domain,
            'app_user': app_user,
            'enabled': deployment.is_live,
        }

        upload_template(
            filename='app_template/app.pp',
            destination='/usr/share/puppet/manifests/%s.pp' % app.name,
            context=context,
            use_jinja=True, template_dir=settings.JINJA2_TEMPLATE_DIR,
            use_sudo=True)

        command = ' '.join([
            settings.PUPPET_BIN,
            'apply',
            '--modulepath=/usr/share/puppet/modules/',
            '/usr/share/puppet/manifests/%s.pp' % app.name,
        ])
        result = sudo(command, combine_stderr=False)

        if result.failed:
            raise Exception(result.return_code, result.stderr)

        if deployment.is_live and not app_user.notified:
            enqueue(notify_user, deployment)

    finally:
        disconnect_all()


@raven
def notify_user(deployment, **kwargs):
    from django.template.loader import render_to_string
    from django.core.mail import send_mail

    host = deployment.gunicorn_instances.get().service.host
    app = deployment.application
    domain = '%s.%s' % (app.name, host.realm.base_domain)
    user = deployment.user_instances.get()

    context = {
        'app': app,
        'app_domain': domain,
        'user': user,
    }

    subject = render_to_string('mail/deployed_subject.txt', context)
    body = render_to_string('mail/deployed_body.txt', context)

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
        [user.email], fail_silently=False)

    user.notified = True
    user.save()


def close_connection():
    """Close the connection only if not in eager mode"""
    if not settings.RQ.get('eager', True):
        connection.close()
