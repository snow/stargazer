#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import sys
import json
import pprint
from datetime import datetime

from pyrcp.django.cli import setup_env

settings = setup_env(__file__)

from django.contrib.auth.models import User
from core.models import Post, Author, UserProfile

def load_users(file):
    print '\nimporting users'
    for e in json.load(file):
        try:
            user = User.objects.filter(username=e['username']).get()
        except User.DoesNotExist:
            user = User.objects.create_user(e['username'], e['email'], 'asdfgh')
            user.save()
            
            profile = UserProfile(user=user)
            profile.save()
            
        print '.',
        sys.stdout.flush()
        
def load_authors(file):     
    print '\nimporting authors'  
    for e in json.load(file):
        try:
            author = Author.objects.filter(name=e['name'], source=e['source']).get()
        except Author.DoesNotExist:
            author = Author(name=e['name'],
                            avatar_uri=e['avatar_uri'],
                            source=e['source'],
                            external_id=e['external_id'])
            
            if e['owner_name']:
                user = User.objects.filter(username=e['owner_name']).get()
                author.owner = user
            
            author.save()
            
        print '.',
        sys.stdout.flush() 
        
def load_posts(file):    
    print '\nimporting posts'   
    for e in json.load(file):
        created = datetime.strptime(e['created'], '%Y-%m-%d %H:%M%S')
        author = Author.objects.filter(name=e['author_name'], source=e['author_source']).get()
        
        try:
            post = Post.objects.filter(content=e['content'], 
                                       author=author, 
                                       created=created).get()
        except Post.DoesNotExist:
            post = Post(content=e['content'],
                        latitude=float(e['latitude']),
                        longitude=float(e['longitude']),
                        address=e['address'],
                        created=created,
                        source=e['source'],
                        external_id=e['external_id'],
                        external_data=e['external_data'])
            
            post.author = author            
            post.save()
            
        print '.',
        sys.stdout.flush()         

if '__main__' == __name__:
    #datafile = open(settings.PROJECT_ROOT + '/data/user_file.txt', 'w')
    pp = pprint.PrettyPrinter(indent=4)
    
    with open(settings.PROJECT_ROOT + '/data/user_file.txt', 'r') as file:
        load_users(file)
        
    with open(settings.PROJECT_ROOT + '/data/author_file.txt', 'r') as file:
        load_authors(file)    
    
    with open(settings.PROJECT_ROOT + '/data/post_file.txt', 'r') as file:
        load_posts(file)
    