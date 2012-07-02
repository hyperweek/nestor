"""
nestor.models
~~~~~~~~~~~~~

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django.db import models
from django.template.defaultfilters import slugify

from django_extensions.db.fields.json import JSONField

from .decorators import enqueue
from .tasks import setup_and_deploy

PRIORITIES = (
    ("1", "high"),
    ("2", "medium"),
    ("3", "low"),
    ("4", "deferred"),
)


class RequestManager(models.Manager):

    def non_deferred(self):
        """
        the requests in the queue not deferred
        """

        return self.filter(priority__lt="4")

    def deferred(self):
        """
        the deferred requests in the queue
        """

        return self.filter(priority="4")

    def retry_deferred(self, new_priority=2):
        count = 0
        for request in self.deferred():
            if request.retry(new_priority):
                request.process()
                count += 1
        return count


class Request(models.Model):
    request_data = JSONField()
    when_added = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=1, choices=PRIORITIES, default="2")

    objects = RequestManager()

    class Meta:
        abstract = True

    def defer(self):
        self.priority = "4"
        self.save()

    def retry(self, new_priority=2):
        if self.priority == "4":
            self.priority = new_priority
            self.save()
            return True
        else:
            return False

    def process(self):
        enqueue(setup_and_deploy, self)


class WufooRequest(Request):
    wufoo_id = models.PositiveIntegerField(unique=True)

    def __unicode__(self):
        return u"Request %s from %s" % (self.network_name, self.company)

    @property
    def network_name(self):
        return slugify(self.request_data['Field3'])

    @property
    def company(self):
        return self.request_data['Field5']

    @property
    def email(self):
        return self.request_data['Field129']

    @property
    def username(self):
        return self.email.split('@')[0].split('+')[0]

    @property
    def first_name(self):
        return self.request_data['Field19']

    @property
    def last_name(self):
        return self.request_data['Field20']
