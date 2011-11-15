import logging

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
    

class PostManagerGeoMixin(models.Manager):
    def nearby(self, lat, lng, range=2000):
        lat_offset = geo.get_lat_offset_by_distance(range)
        lng_offset = geo.get_lng_offset_by_distance(range, lat)
        
        return super(RecentPostManager, self).get_query_set().\
                filter(latitude__gte=lat-lat_offset).\
                filter(latitude__lte=lat+lat_offset).\
                filter(longitude__gte=lng-lng_offset).\
                filter(longitude__lte=lng+lng_offset)

class RecentPostManager(PostManagerGeoMixin):
    def nearby(self, lat, lng, range=2000):
        return super(RecentPostManager, self).nearby(lat, lng, range).\
            order_by('-created')
    
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
    
    recent = RecentPostManager()