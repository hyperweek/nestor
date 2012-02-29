"""
nestor.queue.tasks
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""


def setup_and_deploy(request_id, instance_type='trial'):
    from django.conf import settings
    from django.db.models import Count

    from dploi_server.models import (Application, Deployment, UserInstance,
        Gunicorn, GunicornInstance)

    from nestor.models import WufooRequest
    from nestor.queue.client import delay
    from nestor.queue.tasks import deploy

    request = WufooRequest.objects.get(pk=request_id)
    HOST_INSTANCES = getattr(settings, 'HOST_INSTANCES', 20)

    hosts = Gunicorn.objects.filter(is_enabled=True)\
        .annotate(num_instances=Count('instances'))\
        .exclude(num_instances__gte=HOST_INSTANCES)\
        .order_by('-num_instances')

    if not hosts:
        request.defer()
        raise Exception('No host available for request #%s' % request.pk)

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
    instance.service = hosts[0]
    instance.deployment = deployment
    instance.workers = 1
    instance.save()

    delay(deploy, deployment.pk)
    request.delete()


def deploy(deploy_id, force_delete=False, **kwargs):
    """
    Deploy an application to a remote machine.

    First, it generates a puppet manifest, then connect to the
    remote machine and call puppet apply with the generated manifest
    as parameter.
    """
    from django.conf import settings
    from django.template.loader import render_to_string
    from django.core.mail import send_mail

    from fabric.api import env, sudo
    from fabric.contrib.files import upload_template
    from fabric.network import disconnect_all

    from dploi_server.models import Deployment

    try:
        deployment = Deployment.objects.get(pk=deploy_id)
        host = deployment.gunicorn_instances.get().service.host
        app = deployment.application
        domain = '%s.%s' % (app.name, host.realm.base_domain)
        app_user = deployment.user_instances.get()

        SSH_PORT = getattr(settings, 'SSH_PORT', 22)
        SSH_USER = getattr(settings, 'SSH_USER', 'ubuntu')
        SSH_PASSWORD = getattr(settings, 'SSH_PASSWORD', None)

        env.host_string = '%s@%s:%s' % (SSH_USER, host.private_ipv4, SSH_PORT)
        env.user = SSH_USER
        env.password = SSH_PASSWORD
        env.timeout = 60 * 10

        context = {
            'user': env.user,
            'group': env.user,
            'app_name': app.name,
            'app_domain': domain,
            'app_user': app_user,
            'enabled': False if force_delete else deployment.is_live,
        }

        upload_template(
            filename='app_template/app.pp',
            destination='/usr/share/puppet/manifests/%s.pp' % app.name,
            context=context,
            use_jinja=True, template_dir=settings.JINJA2_TEMPLATE_DIR,
            use_sudo=True)

        command = ' '.join([
            'puppet',
            'apply',
            '--modulepath=/usr/share/puppet/modules/',
            '/usr/share/puppet/manifests/%s.pp' % app.name,
        ])
        result = sudo(command, combine_stderr=False)

        if result.failed:
            raise Exception(result.return_code, result.stderr)

        if deployment.is_live and app_user.notified == False:
            subject = render_to_string('mail/deployed_subject.txt', context)
            body = render_to_string('mail/deployed_body.txt', context)

            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                [app_user.email], fail_silently=True)

            app_user.notified = True
            app_user.save()

    finally:
        disconnect_all()
