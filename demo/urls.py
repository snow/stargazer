from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from demo.views import UnderConstructionView, IndexView, CreatePostView,\
                       PostListContainerView, RecentPostListView, \
                       LikePostView, BanPostView, \
                       LatLng2AddrView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('demo.views',
    url(r'^$', IndexView.as_view()),
    
    url(r'^post/create$', login_required(CreatePostView.as_view())),
    
    url(r'^post/(?P<sorter>recent|top|trending)/$', 
        PostListContainerView.as_view()),
    
    url(r'^post/load/recent/', RecentPostListView.as_view()),
    
    url(r'^post/like/$', login_required(LikePostView.as_view())),
    url(r'^post/ban/$', login_required(BanPostView.as_view())),
    
    url(r'^teleport$', UnderConstructionView.as_view()),
    
    url(r'^utils/latlng2addr$', LatLng2AddrView.as_view()),
)