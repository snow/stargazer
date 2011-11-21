from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from demo.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view()),
    
    url(r'^post/create/$', login_required(CreatePostView.as_view())),
    
    url(r'^post/(?P<type>recent|top|trending)/$', 
        PostListContainerView.as_view()),
    
    url(r'^post/load/recent/', RecentPostListView.as_view()),
    url(r'^post/load/by_user/(?P<id>\d+)/', UserPostListView.as_view()),
    
    url(r'^post/like/$', login_required(LikePostView.as_view())),
    url(r'^post/ban/$', login_required(BanPostView.as_view())),
    
    url(r'^user/(?P<pk>\d+)/$', UserProfileView.as_view()),
    url(r'^me/$', login_required(MeView.as_view())),
    
    url(r'^teleport/$', TeleportView.as_view()),
    
    url(r'^utils/latlng2addr/$', LatLng2AddrView.as_view()),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
        {'next_page': '/post/recent/'}),
    url(r'^accounts/signup/$', SignupView.as_view()),
)