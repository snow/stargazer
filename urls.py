from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from core.views import LatLng2AddrView
from thirdparty.twitter.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # on the top for better performance
    url(r'^utils/latlng2addr/$', LatLng2AddrView.as_view()),
    
    url(r'^api/', include('api.urls')),
    
    url(r'^w/', include('webapp.urls')),
    
    url(r'^eva/', include('eva.urls')),
    
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),

    url(r'^thirdparty/twitter/$', IndexV.as_view()),
    
    url(r'^thirdparty/twitter/authorize/$', 
        login_required(AuthorizeV.as_view())),
    url(r'^thirdparty/twitter/authorize_return/$', 
        login_required(AuthorizeReturnV.as_view())),
    url(r'^thirdparty/twitter/authorize_done/$', 
        login_required(AuthorizeDoneV.as_view())),
                       
    url(r'^', include('demo.urls')),
    #url(r'^thirdparty/twitter/signout/$', login_required(SignoutV.as_view())),
    
#    url(r'^thirdparty/twitter/authenticate/$', 
#        login_required(AuthenticateV.as_view()))

    
)