#! /usr/bin/env python
# -*- coding: UTF-8 -*-
from os.path import dirname, abspath
import sys
import re
import pprint

from pyrcp.django.cli import setup_env

settings = setup_env(__file__)

from streaming import SgzStreamListener

if '__main__' == __name__:
    datafile = open(dirname(abspath(__file__)) + '/data.txt', 'r')
    pp = pprint.PrettyPrinter(indent=4)
    
    from core.models import Post
    from core.utils import LatLng2Addr
    
    latlng2addr = LatLng2Addr()
    for post in Post.objects.filter(source=Post.T_TWITTER).all():
        if '' == post.address:
            try:
                post.address = latlng2addr.get(post.latitude, post.longitude)
            except LatLng2Addr.BaseException as e:
                print e
                print post.latitude, post.longitude
            else:
                print post.address
                post.save()
    
#    listener = SgzStreamListener()
#    
#    while True:
#        line = datafile.readline().strip()
#        if '' == line:
#            break
#        
#        if '{' is not line[0]:
#            line = '}1' + line
#            
#        if '}' is not line[-1]:
#            line += '1{'
#        
#        for src in re.split('}\d+{', line):
#            src = src.strip()
#            if '' == src:
#                continue
#            
#            if '{' is not src[0]:
#                src = '{' + src
#            
#            if '}' is not src[-1]:
#                src += '}'
#                
#            try:
#                listener.save_status(src)
#                print '.',
#                sys.stdout.flush()
#            except:
#                print line
#                print src
#                raise
#        
