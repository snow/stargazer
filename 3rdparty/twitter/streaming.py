#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
from os.path import dirname, abspath
from optparse import OptionParser
import re
import json
from datetime import timedelta

from django.core.mail import mail_admins
import tweepy
from tweepy import StreamListener, Stream, BasicAuthHandler
from tweepy.models import Status
from pyrcp.django.cli import setup_env

settings = setup_env(__file__)

from core.models import Author, Post
from core.utils import LatLng2Addr

PID_PATH = '{}/streaming.pid'.format(dirname(abspath(__file__)))

_datafile = open(dirname(abspath(__file__)) + '/data.txt', 'a')

class SgzStreamListener(StreamListener):
    '''TODO'''
    
    def __init__(self, api=None):
        self._latlng2addr = LatLng2Addr()        
        super(SgzStreamListener, self).__init__(api)

    def on_data(self, data):
        '''TODO'''
        #_datafile.write(data+'\n')
        
        if 'in_reply_to_status_id' in data:
            if self.on_status(data) is False:
                return False
        else:
            return super(SgzStreamListener, self).on_data(data)
        
    def on_status(self, data):
        '''TODO'''
        return self.save_status(data)     
        
    def save_status(self, data):
        '''TODO'''        
        status = Status.parse(self.api, json.loads(data))
        
        if not status.geo:
            #_datafile.write(data+'\n')
            return
        
        try:
            author = Author.objects.\
                        filter(source=Author.T_TWITTER, 
                               external_id=status.user.id_str).get()
        except Author.DoesNotExist:
            author = Author(name=status.user.screen_name,
                            avatar_uri=status.user.profile_image_url,
                            source=Author.T_TWITTER,
                            external_id=status.user.id_str)
            author.save()
                                
        try:
            post = Post.objects.\
                    filter(source=Post.T_TWITTER, 
                           external_id=status.id_str).get()
        except Post.DoesNotExist:
            lat = float(status.geo['coordinates'][0])
            lng = float(status.geo['coordinates'][1])
            
            try:
                addr = self._latlng2addr.get(lat, lng)
            except LatLng2Addr.BaseException as e:
                addr = ''
                
            # twitter api response in UTC
            created = status.created_at + timedelta(hours=8)    
            
            post = Post(content=status.text,
                        author=author,
                        latitude=lat,
                        longitude=lng,
                        address=addr,
                        source=Post.T_TWITTER,
                        external_id=status.id_str,
                        external_data=data,
                        created=created)
            post.save()
            
        return

#
# let's jean!
# -------------
#
if '__main__' == __name__:
    opt = OptionParser(usage='tweepyshell [options] <username> <password>')
    opt.add_option('-d', '--debug',
            action='store_true',
            dest='debug',
            help='enable debug mode')
    options, args = opt.parse_args()
    
    if options.debug:
        tweepy.debug()
        
    try:
        pid_file = open(PID_PATH, 'w')
        pid_file.write(str(os.getpid()))
        pid_file.flush()
        
        auth = BasicAuthHandler(settings.TWITTER_ACCOUNT, 
                                settings.TWITTER_PASSWORD)
        listener = SgzStreamListener()
        stream = Stream(auth, listener)
        #stream.filter(locations=(103.9278, 30.5620, 104.2097, 30.7882))
        stream.filter(locations=(97.00, 20.54, 123.02, 42.80, # center
                                 72.74, 26.66, 97.00, 49.43,  # west
                                 115.02, 38.54, 135.50, 53.90)) # ne
        
    except:
        mail_admins('Streaming process dead', sys.exc_info()[0])
        raise    
    finally:
        pid_file.close()
        os.remove(PID_PATH)

# some latlng
# center china
# W 97.00022506644018
# S 20.54311479591141
# E 123.01585006644018
# N 42.805728711206335

# west china
# N 49.43442204194387
# E 97.00022506644018
# S 26.660039107788435
# W 72.74241256644018

# ne china
# N 53.89968583646365
# E 135.49631881644018
# S 38.54198948702897
# W 115.01780319144018

# 成都绕城
# NORTH = 30.78815194486169
# EAST = 104.20965957571752
# SOUTH = 30.56196532267716
# WEST = 103.92779159476049

# 成都三环
# NORTH = 30.727892236416363
# EAST = 104.16683006216772
# SOUTH = 30.593518507620672
# WEST = 103.98229408194311

# 成都二环
# NORTH = 30.696382870376212
# EAST = 104.11661910940893
# SOUTH = 30.617675243998054
# WEST = 104.01980209280737

# 武汉三环
# NORTH = 30.69726852005711
# EAST = 114.47569656302221
# SOUTH = 30.452817211422317
# WEST = 114.15571975638159

# 长沙市区
# NORTH = 28.296672379416197
# EAST = 113.08043289114721
# SOUTH = 28.13603157370264
# WEST = 112.9094581597019

# 青岛市区
# NORTH = 36.228211852897225
# EAST = 120.56658554007299
# SOUTH = 36.029110596631895
# WEST = 120.28403091360815

# 青岛
# NORTH = 37.09
# EAST = 121
# SOUTH = 35.35
# WEST = 119.3

# 郑州 绕城-四环
# NORTH = 34.85072027323119
# EAST = 113.78733444144018
# SOUTH = 34.6346203413782
# WEST = 113.52572250296362