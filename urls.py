from django.conf.urls.defaults import patterns, include, url

from core.views import LatLng2AddrView
from thirdparty.twitter.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
                       
    url(r'^utils/latlng2addr/$', LatLng2AddrView.as_view()),
    
    url(r'^', include('demo.urls'))
)

urlpatterns += patterns('',
    url(r'^thirdparty/twitter/$', IndexV.as_view()),
    url(r'^thirdparty/twitter/authorize/$', AuthorizeV.as_view()),
    url(r'^thirdparty/twitter/authorize_return/$', AuthorizeReturnV.as_view()),
    url(r'^thirdparty/twitter/authenticate/$', AuthenticateV.as_view()),
    url(r'^thirdparty/twitter/signout/$', SignoutV.as_view())
)