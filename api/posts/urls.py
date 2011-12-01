from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from api.posts.views import *

urlpatterns = patterns('',
    url(r'^lat(?P<lat>\d+\.?\d*)/lng(?P<lng>\d+\.?\d*)/'+\
            '(?P<type>recent|top|trending).(?P<format>json|html)$', 
        ListV.as_view()),
                       
    url(r'^like/(?P<id>\d+)/$', login_required(LikeV.as_view())),
    url(r'^ban/(?P<id>\d+)/$', login_required(BanV.as_view())),
    
    url(r'^create.(?P<format>json|html)$', login_required(CreateV.as_view())),
)