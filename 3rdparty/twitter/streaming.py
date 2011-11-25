#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import sys, os
from os.path import dirname, abspath

from tweepy import StreamListener, Stream, BasicAuthHandler

# settup environment
PROJ_PATH = dirname(dirname(dirname(abspath(__file__))))
PROJ_CONTAINER = dirname(PROJ_PATH)
PROJ_DIR = PROJ_PATH.split('/')[-1]

sys.path.append(PROJ_CONTAINER)
sys.path.append(PROJ_CONTAINER+'/'+PROJ_DIR)

os.environ['DJANGO_SETTINGS_MODULE'] = PROJ_DIR + '.settings'
from django.core.management import setup_environ
from stargazer import settings

setup_environ(settings)

# models
from stargazer.core.models import Post

_datafile = open(dirname(abspath(__file__)) + '/data.txt', 'a')

class SgzStreamListener(StreamListener):
    '''TODO'''

    def on_data(self, data):
        '''TODO'''
        _datafile.write(data)
        return super(SgzStreamListener, self).on_data(data)

    def on_status(self, status):
        '''TODO'''
#        print status
#        print 'user: ', status.from_user
#        try:
#            print 'geo : ', status.geo
#            print 'loc : ', status.location
#        except:
#            pass
#        print 'txt : ', status.text
#        print '-' * 5
        print 'got one'
        return

# some latlng

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

#
# let's jean!
# -------------
#

auth = BasicAuthHandler(settings.TWITTER_ACCOUNT, settings.TWITTER_PASSWORD)
listener = SgzStreamListener()
stream = Stream(auth, listener)
stream.filter(locations=(30.7882, 104.2097, 30.5620, 103.9278))