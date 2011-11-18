from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from demo.views import UnderConstructionView, IndexView, CreatePostView, \
                       PostListContainerView, RecentPostListView, \
                       LikePostView, BanPostView, SignupView, MeView, \
                       LatLng2AddrView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view()),
    
    url(r'^post/create/$', login_required(CreatePostView.as_view())),
    
    url(r'^post/(?P<sorter>recent|top|trending)/$', 
        PostListContainerView.as_view()),
    
    url(r'^post/load/recent/', RecentPostListView.as_view()),
    
    url(r'^post/like/$', login_required(LikePostView.as_view())),
    url(r'^post/ban/$', login_required(BanPostView.as_view())),
    
    url(r'^me/$', login_required(MeView.as_view())),
    
    url(r'^teleport/$', UnderConstructionView.as_view()),
    url(r'^fav/$', UnderConstructionView.as_view()),
    
    url(r'^channel/$', UnderConstructionView.as_view()),
    
    url(r'^utils/latlng2addr$', LatLng2AddrView.as_view()),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', 
        {'next_page': '/post/recent/'}),
    url(r'^accounts/signup/$', SignupView.as_view()),
)