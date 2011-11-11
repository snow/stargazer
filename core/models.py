from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ExternalAccount(models.Model):
    TYPES = ((0, 'local'),
             (1, 'twitter'),
             (2, 'flickr'))
    
    type = models.PositiveSmallIntegerField(choices=TYPES)
    external_id = models.CharField(max_length=255)
    name = models.CharField(max_length=20)
    avatar_uri = models.CharField(max_length=255)
    
    owner = models.ForeignKey(User, null=True, blank=True, default=None)
    token = models.CharField(max_length=255, blank=True)
     
     
class Author(models.Model):    
    name = models.CharField(max_length=20)
    avatar_uri = models.CharField(max_length=255)
    source = models.PositiveSmallIntegerField(choices=ExternalAccount.TYPES)
    
    account = models.ForeignKey(User, null=True, blank=True, default=None)
    ext_account = models.ForeignKey(ExternalAccount, null=True, blank=True, 
                                    default=None)
    
    
class Post(models.Model):
    '''A post'''
    content = models.CharField(max_length=200)
    
    author = models.ForeignKey(Author)
    
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    address = models.CharField(max_length=100)
    
    created = models.DateTimeField(auto_now_add=True)
    
    likes = models.ManyToManyField(User, related_name='likes')
    bans = models.ManyToManyField(User, related_name='bans')    