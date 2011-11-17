# -*- coding: UTF-8 -*-
import urllib2
import json
import logging

from django.views.generic import View, TemplateView, CreateView, ListView
from django.http import HttpResponse
from django.forms import ModelForm, Textarea, HiddenInput
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import urlquote

from core.models import Post, Author

l = logging.getLogger(__name__)

class UnderConstructionView(TemplateView):
    template_name = 'demo/under_construction.html'

class IndexView(TemplateView):
    template_name = 'demo/index.html'

class CreatePostView(CreateView):
    class PostForm(ModelForm):
        class Meta:
            model = Post
            fields = ('content', 'latitude', 'longitude', 'address')
            widgets = {
                'content': Textarea(),
                'latitude': HiddenInput(),
                'longitude': HiddenInput(),
                'address': HiddenInput()
            }
            
    form_class = PostForm
    initial = {
        'content': 'What\'s on ur mind?'
    }
    template_name = 'demo/post/create.html'
    
    user = False
    
    def post(self, request, *args, **kwargs):
        self.user = request.user
        return super(CreateView, self).post(request, *args, **kwargs)
    
    def form_valid(self, form):
        post = form.instance
        
        if 0 == self.user.author_set.filter(source=Author.T_LOCAL).count():
            author = Author(name=self.user.username, source=Author.T_LOCAL, 
                            owner=self.user)
            author.save()
        else:
            author = self.user.author_set.filter(source=Author.T_LOCAL).get()
            
        post.author = author

        self.success_url = '/post/recent/?'+\
            'addr=%(address)s&lat=%(latitude)s&lng=%(longitude)s'
        
        return super(CreateView, self).form_valid(form)
    

class PostListContainerView(TemplateView):
    template_name = 'demo/post/list.html'
    
    def dispatch(self, request, *args, **kwargs):
        kwargs['lat'] = request.GET.get('lat', '')
        kwargs['lng'] = request.GET.get('lng', '')
        kwargs['addr'] = request.GET.get('addr', '')
        
        return super(PostListContainerView, self).dispatch(request, *args, 
                                                           **kwargs)
    
class RecentPostListView(ListView):
    template_name = 'demo/post/list_content.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.lat = float(request.GET['lat'])
        self.lng = float(request.GET['lng'])
        self.queryset = Post.recent.with_user(request.user).nearby(self.lat, self.lng).all()
        
        return super(RecentPostListView, self).dispatch(request, *args, 
                                                        **kwargs)
        
class LikePostView(View):
    '''TODO'''
    def post(self, request):
        post = Post.objects.get(pk=request.POST['id'])
        if 0 == post.likes.filter(id=request.user.id).count():
            post.likes.add(request.user)
            act = 'added'
        else:
            post.likes.remove(request.user)
            act = 'removed'
            
        return HttpResponse(json.dumps({
                                'done': True,
                                'act': act,
                            }), 
                            content_type='application/json')

class BanPostView(View):        
    '''TODO'''
    def post(self, request):
        post = Post.objects.get(pk=request.POST['id'])
        if 0 == post.bans.filter(id=request.user.id).count():
            post.bans.add(request.user)
            act = 'added'
        else:
            post.bans.remove(request.user)
            act = 'removed'
            
        return HttpResponse(json.dumps({
                                'done': True,
                                'act': act,
                            }), 
                            content_type='application/json')
    
class LatLng2AddrView(View):
    API_URI = 'http://maps.googleapis.com/maps/api/geocode/json'
    
    API_RETRY_LIMIT = 3
    retry_count = 0
    
    def call_api(self, lat, lng):
        try:
            api_resp = urllib2.urlopen(self.API_URI+
                '?latlng={},{}&language=zh-CN&sensor=false'.format(lat, lng))
            
        except urllib2.URLError as err:
            if self.retry_count < self.API_RETRY_LIMIT:
                retry_count += 1
                return self.call_api(lat, lng)
            else:
                raise Exception('failed to connect Google Geocoding service')
        else:
            result = json.loads(api_resp.read())
    
            if 'OK' == result['status']:
                return result['results']
    
            # exceptions
            elif 'ZERO_RESULTS' == result['status'] or \
                 'NOT_FOUND' == result['status']:
                raise Exception('failed geocoding by Google Geocoding service')
            
            else:
                raise Exception('unregonized response from '+
                              'Google Geocoding service')
            
    def process_api_results(self, results):
        result = results[0]
    
        address = ''
        
        for com in result['address_components']:
            address = com['short_name'] + ' ' + address            
            if 'sublocality' in com['types']:
                break
        
        return address
    
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            self.process_api_results(
                self.call_api(request.GET['lat'], request.GET['lng'])))