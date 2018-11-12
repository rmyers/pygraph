from django.conf import settings
from django.db import models
from django.utils import timezone


class Game(models.Model):

    start = models.DateTimeField()
    end = models.DateTimeField()

    class Meta:
        ordering = ['-end']
        get_latest_by = 'end'

    def __unicode__(self):
        return 'Julython %s' % self.end.year

    @classmethod
    def active(cls, now=None):
        """Returns the active game or None."""
        now = now or timezone.now()
        try:
            return cls.objects.get(start__lte=now, end__gte=now)
        except cls.DoesNotExist:
            return None

    @classmethod
    def active_or_latest(cls, now=None):
        """Return the an active game or the latest one."""
        now = now or timezone.now()
        game = cls.active(now)
        if game is None:
            query = cls.objects.filter(end__lte=now)
            if len(query):
                game = query[0]
        return game


class Commit(models.Model):
    """
    Commit record for the profile, the parent is the profile
    that way we can update the commit count and last commit timestamp
    in the same transaction.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    hash = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    message = models.CharField(max_length=2024, blank=True)
    url = models.CharField(max_length=512, blank=True)
    timestamp = models.DateTimeField(db_index=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'Commit: %s' % self.hash
