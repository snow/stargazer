import logging
import hashlib

from django.db import models
from django.contrib.auth.models import User

from pyrcp import geo

l = logging.getLogger(__name__)

# Create your models here.
#class ExternalAccount(models.Model):
#    TYPES = ((0, 'local'),
#             (1, 'twitter'),
#             (2, 'flickr'))
#
#    type = models.PositiveSmallIntegerField(choices=TYPES)
#    external_id = models.CharField(max_length=255)
#    name = models.CharField(max_length=20)
#    avatar_uri = models.CharField(max_length=255)
#
#    owner = models.ForeignKey(User, null=True, blank=True, default=None)
#    token = models.CharField(max_length=255, blank=True)
def _get_gavatar_uri(email):
    return 'http://www.gravatar.com/avatar/{}?s=48&d=monsterid'.\
            format(hashlib.md5(email.strip().lower()).hexdigest())

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    def gavatar_uri(self):
        return _get_gavatar_uri(self.user.email)

class Author(models.Model):
    T_LOCAL = 0
    T_TWITTER = 1
    T_FLICKER = 2

    TYPES = ((T_LOCAL, 'local'),
             (T_TWITTER, 'twitter'),
             (T_FLICKER, 'flickr'))

    name = models.CharField(max_length=20)
    avatar_uri = models.CharField(max_length=255, blank=True)

    source = models.PositiveSmallIntegerField(choices=TYPES)

    # for local account
    owner = models.ForeignKey(User, null=True, blank=True, default=None)

    # for external account
    external_id = models.CharField(max_length=255, blank=True)
    token = models.CharField(max_length=255, blank=True)

    def gavatar_uri(self):
        return _get_gavatar_uri(self.owner.email)


class PostManager(models.Manager):
    _queryset = None

    def _get_query_set(self):
        if None is self._queryset:
            self._queryset = super(PostManager, self).get_query_set()

        return self._queryset

    def _update_query_set(self, queryset):
        self._queryset = queryset

    def get_query_set(self):
        if None is self._queryset:
            return super(PostManager, self).get_query_set()
        else:
            tmp = self._queryset
            self._queryset = None
            return tmp

    def recent(self):
        self._update_query_set(self._get_query_set().order_by('-created'))

        return self

    def with_user(self, user):
        self.model.current_user = user
        self._update_query_set(
            self._get_query_set().exclude(bans=self.model.current_user))

        return self

    def by_user(self, user):
        if type(user) is str:
            user = int(user)

        if type(user) is int:
            user = User.objects.get(pk=user)

        self._update_query_set(
            self._get_query_set().filter(author__owner=user))

        return self

    def nearby(self, lat, lng, range=2000):
        lat_offset = geo.get_lat_offset_by_distance(range)
        lng_offset = geo.get_lng_offset_by_distance(range, lat)

        self._update_query_set(
            self._get_query_set().filter(latitude__gte=lat-lat_offset).
                                filter(latitude__lte=lat+lat_offset).
                                filter(longitude__gte=lng-lng_offset).
                                filter(longitude__lte=lng+lng_offset))
        return self


class Post(models.Model):
    '''A post'''
    SCENARIO_DEFAULT = 0
    SCENARIO_UG = 0

    SCENARIOS = (SCENARIO_DEFAULT, SCENARIO_UG)

    scenario = SCENARIO_DEFAULT

    content = models.CharField(max_length=200)

    author = models.ForeignKey(Author)

    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    address = models.CharField(max_length=100)

    created = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name='likes')
    bans = models.ManyToManyField(User, related_name='bans')

    objects = PostManager()

    current_user = False

    def is_liked(self):
        return Post.current_user and \
            self.likes.filter(id=Post.current_user.id).exists()