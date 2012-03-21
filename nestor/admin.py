"""
nestor.admin
~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import logging

from django.conf import settings
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.admin.util import unquote
from django.utils.functional import update_wrapper
from django.contrib import messages

from dnsimple.api import DNSimple

from dploi_server.models import Deployment, Host
from dploi_server.admin import DeploymentAdmin as DeploymentAdminLegacy
from dploi_server.admin import HostAdmin as HostAdminLegacy

from nestor.models import WufooRequest
from nestor.commands import deploy

logger = logging.getLogger('nestor')


class WufooRequestAdmin(admin.ModelAdmin):
    list_display = ('wufoo_id', 'network_name', 'company', 'when_added', 'priority')
    list_filter = ['priority', 'when_added']
    ordering = ('-when_added',)
    date_hierarchy = 'when_added'

    def user(self, obj):
        return u"%s %s <%s>" % (obj.first_name, obj.last_name, obj.email)
    user.short_description = _('user')

admin.site.register(WufooRequest, WufooRequestAdmin)


class HostAdmin(HostAdminLegacy):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(?P<object_id>.+)/register/$',
                wrap(self.register_view),
                name='%s_%s_apply' % info),
        )

        urlpatterns += super(HostAdmin, self).get_urls()
        return urlpatterns

    def register_view(self, request, object_id, **kwargs):
        obj = get_object_or_404(self.model, pk=unquote(object_id))

        try:
            base_domain = obj.realm.base_domain
            host_domain = '%s.%s' % (obj.name, base_domain)

            if settings.USE_DNSSIMPLE:
                dns = DNSimple(settings.DNSIMPLE_USER, settings.DNSIMPLE_PASSWORD)
                domain = dns.domains[base_domain]
                response = domain.add_record(obj.name, 'A', obj.public_ipv4)

            if response:
                messages.success(request,
                    _('Added record: %s A %s' % (host_domain, obj.public_ipv4)))
            else:
                messages.error(request,
                    _('Failed to add record: %s A %s' % (host_domain, obj.public_ipv4)))
        except Exception, e:
            messages.error(request, str(e))

        opts = obj._meta
        info = opts.app_label, opts.module_name
        return HttpResponseRedirect(reverse('admin:%s_%s_changelist' % info))

admin.site.unregister(Host)
admin.site.register(Host, HostAdmin)


class DeploymentAdmin(DeploymentAdminLegacy):
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns('',
            url(r'^(?P<object_id>.+)/apply/$',
                wrap(self.apply_view),
                name='%s_%s_apply' % info),
        )

        urlpatterns += super(DeploymentAdmin, self).get_urls()
        return urlpatterns

    def apply_view(self, request, object_id, **kwargs):
        obj = get_object_or_404(self.model, pk=unquote(object_id))
        try:
            deploy(obj)
            messages.success(request, _('Deploying ...'))
        except Exception, e:
            logger.exception(u'Error applying deployment: %s', e)
            messages.error(request, u'Error applying deployment: %s' % e)

        opts = obj._meta
        info = opts.app_label, opts.module_name
        return HttpResponseRedirect(reverse('admin:%s_%s_changelist' % info))

admin.site.unregister(Deployment)
admin.site.register(Deployment, DeploymentAdmin)
