from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from webapp.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexV.as_view()),
    
    url(r'^posts/nearby/(?P<type>recent|top|trending)/$', ListV.as_view()),
    url(r'^posts/lat(?P<lat>\d+\.?\d*)/lng(?P<lng>\d+\.?\d*)/'+\
        '(?P<type>recent|top|trending)/$', ListV.as_view()),
                       
    url(r'^posts/create/$', login_required(CreateV.as_view())),                   
                       
    url(r'^teleport/$', TeleportV.as_view()),
    
    url(r'^signin/$', SigninV.as_view()),
    url(r'^signup/$', SignupV.as_view()),

#    url(r'^post/load/recent/', RecentPostListView.as_view()),
#    url(r'^post/load/by_user/(?P<id>\d+)/', UserPostListView.as_view()),
#
#    url(r'^post/like/$', login_required(LikePostView.as_view())),
#    url(r'^post/ban/$', login_required(BanPostView.as_view())),
#
#    url(r'^user/(?P<pk>\d+)/$', UserProfileView.as_view()),
#    url(r'^me/$', login_required(MeView.as_view())),
 
#    url(r'^accounts/signup/$', SignupView.as_view()),
)