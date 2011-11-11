from django.conf.urls.defaults import patterns, include, url

from demo.views import UnderConstructionView, IndexView, CreatePostView, LatLng2Addr

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('demo.views',
    url(r'^$', IndexView.as_view()),
    
    url(r'^post/create', CreatePostView.as_view()),
    
    url(r'^post/recent/', UnderConstructionView.as_view()),
    url(r'^post/top/', UnderConstructionView.as_view()),
    url(r'^post/trending/', UnderConstructionView.as_view()),
    
    url(r'^teleport$', UnderConstructionView.as_view()),
    
    url(r'^utils/latlng2addr$', LatLng2AddrView.as_view()),
)
