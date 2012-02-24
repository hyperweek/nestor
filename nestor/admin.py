from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.admin.util import unquote
from django.utils.functional import update_wrapper
from django.contrib import messages

from dploi_server.models import Deployment
from dploi_server.admin import DeploymentAdmin as DeploymentAdminLegacy


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
        # TODO: handle delayed task
        messages.success(request, _('Deploying ...'))

        opts = obj._meta
        info = opts.app_label, opts.module_name
        return HttpResponseRedirect(reverse('admin:%s_%s_changelist' % info))

admin.site.unregister(Deployment)
admin.site.register(Deployment, DeploymentAdmin)
