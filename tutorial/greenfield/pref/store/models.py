
import json
import uuid
from typing import List, Any, NamedTuple

from django.core.exceptions import ValidationError
from django.db import models
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from .kinds import KindController, KIND_CHOICES, KINDS


class InvalidSite(Exception):
    pass


class InvalidKey(Exception):
    pass


class Preference(NamedTuple):
    """Our preferences are the union of the site defaults and overrides"""
    site_url: str
    user_id: str
    kind: str
    key: str
    value: Any

    @property
    def _kind(self) -> KindController:
        return KINDS[self.kind]

    def serialize(self, new_value: Any) -> str:
        return self._kind.serialize(new_value)

    def deserialize(self) -> Any:
        return self._kind.deserialize(self.value)


class Site(models.Model):
    """A website that uses preferences."""

    url = models.URLField(primary_key=True)
    auth_url = models.URLField()

    def __str__(self) -> str:
        return self.url


class Serializable(models.Model):
    """Abstract model which provides methods to handle our custom fields."""

    kind = models.CharField(
        max_length=10,
        choices=KIND_CHOICES,
        blank=False,
        null=False,
    )
    value = models.TextField()

    class Meta:
        abstract = True

    @property
    def _kind(self) -> KindController:
        return KINDS[self.kind]

    def serialize(self, new_value: str = None) -> str:
        if new_value is None:
            return self._kind.serialize(self.value)
        return self._kind.serialize(new_value)

    def deserialize(self) -> Any:
        return self._kind.deserialize(self.value)

    def get_cache_key(self) -> str:
        raise NotImplementedError('Subclasses must provide `get_cache_key`')

    def clean(self):
        # If we do not have a kind don't bother checking the default field.
        if not self.kind:
            return
        try:
            # Make sure our default value will deserialize properly
            string_value = self.deserialize()
            self.serialize(string_value)
        except ValueError:
            raise ValidationError({'value': _('Unable to deserialize value')})
        except json.decoder.JSONDecodeError:
            raise ValidationError({'value': _('Unable to decode JSON object')})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear the cache for our site defaults. Allows us to use the
        # django admin to create these models, and still work with our
        # custom site controller.
        _cache_key = self.get_cache_key()
        cache.delete(_cache_key)

    def delete(self, *args, **kwargs):
        # Clear the cache for our site defaults. Allows us to use the
        # django admin to create these models, and still work with our
        # custom site controller.
        _cache_key = self.get_cache_key()
        cache.delete(_cache_key)
        super().delete(*args, **kwargs)


class Kind(Serializable):
    """An available preference for a site."""

    site = models.ForeignKey('Site', on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    deprecated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.site} - {self.key}'

    def get_cache_key(self) -> str:
        return SiteController.defaults_cache_key(self.site)

    def to_preference(self, user_id) -> Preference:
        return Preference(self.site.pk, user_id, self.kind, self.key, self.deserialize())


class Override(Serializable):
    """A instance of a preference that has been explicitly set."""

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey('Site', on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255)
    key = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['site', 'user_id'], name='site_user_idx'),
            models.Index(fields=['user_id'], name='user_id_idx'),
        ]

    def __str__(self) -> str:
        return self.key

    def to_preference(self) -> Preference:
        return Preference(self.site.pk, self.user_id, self.kind, self.key, self.deserialize())

    def get_cache_key(self) -> str:
        return PreferenceController.cache_key(self.site, self.user_id)


def get_user_id(auth_url: str, token: str) -> str:
    pass


class PreferenceController:
    """Preference Controller

    This serves three purposes. First it authenticates the user token
    against the requested site's auth_url. Second we check cache for a stored
    response. Lastly we preform the request and update caches as needed.

    We don't use Django users, because we don't care or want to store users
    in our database. The identity service is responsible for that. We only
    store the unique user_id in our tables.
    """

    @classmethod
    def get_user_id(cls, site_url: str, token: str) -> str:
        auth_url = SiteController.auth_url(site_url)
        assert auth_url
        # try to auth or raise an error
        return auth_url

    @classmethod
    def cache_key(cls, site_url: str, user_id: str) -> str:
        return f'preferences:{site_url}:{user_id}'

    @classmethod
    def get(
        cls,
        auth_token: str,
        site_url: str,
    ) -> List[Preference]:

        user_id = cls.get_user_id(site_url=site_url, token=auth_token)
        _cache_key = cls.cache_key(site_url, user_id)
        results = cache.get(_cache_key)
        if results is None:
            # Gather all the defaults for the site then merge in overrides.
            defaults = SiteController.defaults(site_url=site_url)
            preferences_from_defaults = map(
                lambda default: default.to_preference(user_id),
                defaults
            )
            preference_mapping = {p.key: p for p in preferences_from_defaults}

            # Gather any overrides and update the mapping
            overrides = Override.objects.filter(site__pk=site_url, user_id=user_id)
            preferences_from_overrides = map(
                lambda override: override.to_preference(),
                overrides
            )
            override_mapping = {p.key: p for p in preferences_from_overrides}

            preference_mapping.update(override_mapping)
            results = list(preference_mapping.values())
            cache.set(_cache_key, results, 600)
        return results

    @classmethod
    def update(
        cls,
        auth_token: str,
        site_url: str,
        key: str,
        value: Any,
    ) -> Preference:
        """Create or Delete an Override.

        Since we have the concept of a default for any given preference we only
        need to store items that are different than the default. So when we
        'update' a preference we first check to see if the value is equal to
        the default and either drop the request on the floor or remove the
        custom override we have set.
        """
        user_id = cls.get_user_id(site_url=site_url, token=auth_token)
        site_default = SiteController.default_for_key(site_url=site_url, key=key)

        # First we need to check that the value is the correct type and
        # determine if we need to add/remove an override for the value.
        default_for_site = site_default.serialize()
        kind = site_default.kind

        try:
            serialize_custom_value = site_default.serialize(value)
        except Exception:
            raise ValueError(f'Expected {kind} for key {key}')

        reset_to_default = (default_for_site == serialize_custom_value)

        if reset_to_default:
            Override.objects.filter(
                site__pk=site_url,
                user_id=user_id,
                key=key,
            ).delete()
            return site_default.to_preference(user_id=user_id)

        site = SiteController.get(site_url=site_url)
        override, _created = Override.objects.update_or_create(
            site=site,
            user_id=user_id,
            kind=kind,
            key=key,
            defaults={'value': serialize_custom_value}
        )
        return override.to_preference()


class SiteController:

    @classmethod
    def cache_key(cls, site_url: str) -> str:
        return f'site:{site_url}'

    @classmethod
    def get(cls, site_url: str) -> Site:
        _cache_key = cls.cache_key(site_url)
        site = cache.get(_cache_key)
        if site is None:
            try:
                site = Site.objects.get(url=site_url)
            except Site.DoesNotExist:
                raise InvalidSite
            cache.set(_cache_key, site, 60 * 60)
        return site

    @classmethod
    def auth_url_cache_key(cls, site_url: str) -> str:
        return f'site_auth_url:{site_url}'

    @classmethod
    def auth_url(cls, site_url: str) -> str:
        _cache_key = cls.auth_url_cache_key(site_url)
        auth_url = cache.get(_cache_key)
        if auth_url is None:
            site = cls.get(site_url=site_url)
            auth_url = site.auth_url
            # The auth url should almost never change, so set a long ttl
            cache.set(_cache_key, auth_url, 60 * 60 * 24 * 30)
        return auth_url

    @classmethod
    def defaults_cache_key(cls, site_url: str) -> str:
        return f'site_defaults:{site_url}'

    @classmethod
    def defaults(cls, site_url: str) -> List[Kind]:
        site = cls.get(site_url)
        _cache_key = cls.defaults_cache_key(site_url)
        defaults = cache.get(_cache_key)
        if defaults is None:
            defaults = list(Kind.objects.filter(site=site))
            cache.set(_cache_key, defaults, 60 * 60)
        return defaults

    @classmethod
    def default_for_key(cls, site_url: str, key: str) -> Kind:
        site = cls.get(site_url)
        try:
            default = Kind.objects.get(site=site, key=key)
        except Kind.DoesNotExist:
            raise InvalidKey

        return default
