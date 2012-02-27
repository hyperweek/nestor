"""
nestor.queue.tasks
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""


def deploy(deployment, **kwargs):
    """
    Deploy an applicaiton to a remote machine.

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

    try:
        host = deployment.gunicorn_instances.get().service.host
        app = deployment.application
        domain = '%s.%s' % (app.name, host.realm.base_domain)
        app_user = deployment.user_instances.get()

        SSH_PORT = getattr(settings, 'SSH_PORT', 22)
        SSH_USER = getattr(settings, 'SSH_USER', 'ubuntu')
        SSH_PASSWORD = getattr(settings, 'SSH_PASSWORD', '')

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
            'is_live': deployment.is_live,
        }

        upload_template(
            filename='app_template/app.pp',
            destination='/usr/share/puppet/manifests/%s.pp' % app,
            context=context,
            use_jinja=True, template_dir=settings.JINJA2_TEMPLATE_DIR,
            use_sudo=True)

        command = ' '.join([
            'puppet',
            'apply',
            '--modulepath=/usr/share/puppet/modules/',
            '/usr/share/puppet/manifests/%s.pp' % app,
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
