"""
nestor.admin
~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import logging

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

import reversion
from dnsimple.api import DNSimple

from dploi_server.models import Deployment, Host
from dploi_server.admin import DeploymentAdmin as DeploymentAdminLegacy
from dploi_server.admin import HostAdmin as HostAdminLegacy

from nestor.models import WufooRequest
from nestor.commands import deploy

logger = logging.getLogger('nestor')


class WufooRequestAdmin(reversion.VersionAdmin):
    list_display = ('wufoo_id', 'network_name', 'company', 'when_added', 'priority')
    list_filter = ['priority', 'when_added']
    ordering = ('-when_added',)
    date_hierarchy = 'when_added'

    def user(self, obj):
        return u"%s %s <%s>" % (obj.first_name, obj.last_name, obj.email)
    user.short_description = _('user')

admin.site.register(WufooRequest, WufooRequestAdmin)


class HostAdmin(HostAdminLegacy):
    actions = ['delete_selected', 'register']

    def register(self, request, queryset):
        for obj in queryset:
            try:
                base_domain = obj.realm.base_domain

                if settings.USE_DNSSIMPLE:
                    dns = DNSimple(settings.DNSIMPLE_USER, settings.DNSIMPLE_PASSWORD)
                    domain = dns.domains[base_domain]
                    success = domain.add_record(obj.name, 'A', obj.public_ipv4)

                if success:
                    messages.success(request,
                        _('Added record: %s A %s' % (obj.hostname, obj.public_ipv4)))
                else:
                    messages.error(request,
                        _('Failed to add record: %s A %s' % (obj.hostname, obj.public_ipv4)))
            except Exception, e:
                messages.error(request, str(e))
    register.short_description = "Register selected host to DNS"

admin.site.unregister(Host)
admin.site.register(Host, HostAdmin)


class DeploymentAdmin(DeploymentAdminLegacy):
    actions = ['delete_selected', 'apply']

    def apply(self, request, queryset):
        for obj in queryset:
            try:
                deploy(obj)
                messages.success(request, _('Deploying %s...' % obj.identifier))
            except Exception, e:
                logger.exception(u'Error deploying %s: %s' % (obj.identifier, e), e)
                messages.error(request, u'Error deploying %s: %s' % (obj.identifier, e))
    apply.short_description = "Deploy selected instances"

admin.site.unregister(Deployment)
admin.site.register(Deployment, DeploymentAdmin)
