# -*- coding: UTF-8 -*-
import urllib2
import json
import logging

from django.views.generic import View, TemplateView, CreateView, ListView, \
                                 FormView, DetailView, RedirectView
from django.http import HttpResponse
from django.forms import ModelForm, Textarea, HiddenInput
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.http import urlquote
from django.contrib.auth.forms import UserCreationForm
from django import forms

from core.models import Post, Author, UserProfile
from core.utils import LatLng2Addr

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
        mgr = Post.objects.nearby(float(request.GET['lat']),
                                  float(request.GET['lng'])).recent()

        if request.user.is_authenticated():
            mgr.with_user(request.user)

        self.queryset = mgr.all()

        return super(RecentPostListView, self).get(request, *args, **kwargs)

class UserPostListView(ListView):
    template_name = 'demo/post/list_content_simple.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Post.objects.by_user(kwargs['id']).recent().all()

        return super(UserPostListView, self).get(request, *args, **kwargs)

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

class MeView(RedirectView):
    permanent = False
    query_string = True

    def get(self, request, *args, **kwargs):
        self.url = '/user/{}/'.format(request.user.id)

        return super(MeView, self).get(request, *args, **kwargs)

class UserProfileView(DetailView):
    model = User
    template_name = 'demo/user_profile.html'

class TeleportView(TemplateView):
    template_name = 'demo/teleport.html'

