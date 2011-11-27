#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import pprint

from pyrcp.django.cli import setup_env

settings = setup_env(__file__)

from django.contrib.auth.models import User
from core.models import Post, Author, UserProfile

def export_users(file):
    json.dump(
        [dict({
            'username': e.username,
            'email': e.email
        }) for e in User.objects.all()], file)
    
def export_authors(file):
    ls = []
    for e in Author.objects.all():
        item = dict({
            'name': e.name,
            'avatar_uri': e.avatar_uri,
            'source': e.source,
            'external_id': e.external_id
        })
        
        if e.owner:
            item['owner_name'] = e.owner.username
        else:
            item['owner_name'] = ''
            
        ls.append(item)
    
    json.dump(ls, file)    
    
def export_posts(file):
    json.dump(
        [dict({
            'content': e.content,
            'author_name': e.author.name,
            'author_source': e.author.source,
            'latitude': str(e.latitude),
            'longitude': str(e.longitude),
            'address': e.address,
            'created': e.created.strftime('%Y-%m-%d %H:%M%S'),
            'source': e.source,
            'external_id': e.external_id,
            'external_data': e.external_data
        }) for e in Post.objects.all()], file)      

if '__main__' == __name__:
    #datafile = open(settings.PROJECT_ROOT + '/data/user_file.txt', 'w')
    #pp = pprint.PrettyPrinter(indent=4)
    
    with open(settings.PROJECT_ROOT + '/data/user_file.txt', 'w') as file:
        export_users(file)
    
    with open(settings.PROJECT_ROOT + '/data/author_file.txt', 'w') as file:
        export_authors(file)
        
    with open(settings.PROJECT_ROOT + '/data/post_file.txt', 'w') as file:
        export_posts(file)
    
    
    
    