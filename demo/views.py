# -*- coding: UTF-8 -*-
import urllib2
import json
import logging

from django.views.generic import View, TemplateView, CreateView, ListView, \
                                 FormView
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm, Textarea, HiddenInput
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.http import urlquote
from django.contrib.auth.forms import UserCreationForm
from django import forms

from core.models import Post, Author, UserProfile

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
        # for passing user to form_valid
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
    
class RecentPostListView(ListView):
    template_name = 'demo/post/list_content.html'
    
    def get(self, request, *args, **kwargs):
        self.lat = float(request.GET['lat'])
        self.lng = float(request.GET['lng'])
        
        if request.user.is_authenticated():        
            self.queryset = Post.recent.with_user(request.user).\
                nearby(self.lat, self.lng).all()
        else:
            self.queryset = Post.recent.nearby(self.lat, self.lng).all()
        
        return super(RecentPostListView, self).get(request, *args, 
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

_USERNAME_HELP = '最多15个字母、数字和 . _ -'        
class SgzUserCreationForm(UserCreationForm):
    '''TODO'''
    username = forms.RegexField(label="用户名", max_length=15, 
        regex=r'^[\w.-]+$', help_text=_USERNAME_HELP, initial=_USERNAME_HELP,
        error_messages = {'invalid': _USERNAME_HELP})
    
    def save(self, commit=True):
        user = super(SgzUserCreationForm, self).save(commit=False)
        user.email = '{}@neverland.cc'.format(user.username)
        if commit:
            user.save()
            profile = UserProfile(user=user)
            profile.save()
            
        return user
                
class SignupView(FormView):
    '''TODO'''
    form_class = SgzUserCreationForm
    template_name = 'registration/signup.html'
    
    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password1'])            
            if user is not None:
                login(request, user)
                self.success_url = request.GET.get('next', '/post/recent')
                return self.form_valid(form)
            else:
                raise Exception('failed to auth newly-created user')
        else:
            return self.form_invalid(form)

class MeView(TemplateView):
    template_name = 'demo/me.html'
    
class TeleportView(TemplateView):
    template_name = 'demo/teleport.html'
    
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
        
        return address.strip()
    
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            self.process_api_results(
                self.call_api(request.GET['lat'], request.GET['lng'])))