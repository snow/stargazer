#! /usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import threading
from datetime import datetime, timedelta
import time
import argparse
import signal
import os
from os.path import dirname, abspath

from tweepy import OAuthHandler, API
from django.conf import settings
from django.core.mail import mail_admins
from pyrcp.django.cli import setup_env

settings = setup_env(__file__)

from django.contrib.auth.models import User
from core.models import Post

PID_PATH = '{}/update_status.pid'.format(dirname(abspath(__file__)))

class Worker(threading.Thread):
    '''TODO'''
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.shutdown_flag = False
        self.service = Service() 
        
    def run(self):
        '''TODO'''
        while not self.shutdown_flag:
            try:
                post, user_profile = self.service.get_post()
            except TypeError:
                time.sleep(10)
            else:
                self.service.update_status(post, user_profile)
    
class Service():
    '''Business logic'''
    
    def __init__(self):    
        self.oauth = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                  settings.TWITTER_CONSUMER_SECRET,
                                  secure=True)
        self.since_id = None
        
    def get_post(self):
        '''Get a post that should push to twitter'''
        twitter_users = User.objects.exclude(userprofile__twitter_key='')        
        qs = Post.objects.filter(source=Post.T_LOCAL, 
                                 author__owner__in=twitter_users).order_by('id')
        if None is self.since_id:
            posts = qs.filter(created__gte=datetime.now()-timedelta(minutes=1))
        else:        
            posts = qs.filter(id__gt=self.since_id)
        
        for post in posts:
            user_profile = post.author.owner.get_profile()
            if args.DEBUG:
                print 'found one post to push: #{} "{}" by {}'.\
                    format(post.id, post.content, post.author.name)
                
            return (post, user_profile)
        
        if args.DEBUG:
            print 'no post to push'    
            
        return None
                
    def update_status(self, post, user_profile):
        '''Push a post to twiter'''
        self.oauth.set_access_token(user_profile.twitter_key, 
                                  user_profile.twitter_secret)
        twitter_post = API(auth_handler=self.oauth).\
                           update_status(status=post.content,
                                         lat=post.latitude,
                                         long=post.longitude)
        post.external_id = twitter_post.id
        post.save()
        
        if args.DEBUG:
            print 'post #{} "{}" by {} pushed to twitter'.\
                format(post.id, post.content, post.author.name)
        
        self.since_id = post.id

def _interrupt_handler(signum, frame):
    if signal.SIGINT == signum:
        raise KeyboardInterrupt
    
def _get_pid():
    try:
        pid_file = open(PID_PATH, 'r')
    except IOError as err:
        if 2 == err.errno:
            return None # pidfile not exist
        else:
            raise # dont know what happend, let propagete
    else:
        pid = int(pid_file.read())
        pid_file.close()
        return pid
        
if '__main__' == __name__:
    parser = argparse.ArgumentParser(description='Push posts to twitter')
    parser.add_argument('ACTION', default='start', nargs='?', 
                        choices=('start', 'stop'))
    parser.add_argument('-d', action='store_true', dest='DEBUG', 
                        help='enable debug mode')
    args = parser.parse_args()
    #print parser.parse_args()
    
    if 'start' == args.ACTION:
        if None is _get_pid():
            pid_file = open(PID_PATH, 'w')
            pid_file.write(str(os.getpid()))
            pid_file.flush()
            # to force SIGINT go to main thread
            signal.signal(signal.SIGINT, _interrupt_handler)
            
            try:
                worker = Worker()
                worker.daemon = True
                worker.start()
                
                while 1 < threading.active_count(): # more threads than the main
                    time.sleep(0.1) # just waiting for KeyboardInterrupt...
            except KeyboardInterrupt:
                if args.DEBUG:
                    print 'shutting down...'
                    
                worker.shutdown_flag = True
                worker.join()
            except:
                mail_admins('Update status service dead', sys.exc_info()[0])
                raise  
            finally:
                pid_file.close()
                os.remove(PID_PATH)
        else:
            print 'update_status service is already running'
        
    elif 'stop' == args.ACTION:        
        pid = _get_pid()
        if None is pid:
            print 'no update_status service running'
        else:
            os.kill(pid, signal.SIGINT)
    
          