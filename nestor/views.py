"""
nestor.views
~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from django_extensions.db.fields.json import JSONDict

from nestor.models import WufooRequest


@require_POST
@csrf_exempt
@transaction.autocommit
def webhook(request, **kwargs):
    req = WufooRequest()
    req.wufoo_id = request.POST['EntryId']
    req.request_data = JSONDict(request.POST.items())
    req.save()

    req.process()
    return HttpResponse('OK')
