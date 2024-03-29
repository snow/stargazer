from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login_required
from django.views.generic import RedirectView

#from core.views import LatLng2AddrView
from thirdparty.twitter.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from core.views import SigninV, SignupV

urlpatterns = patterns('',
    
    url(r'^api/', include('api.urls')),
    
    url(r'^$', RedirectView.as_view(url='/w/', permanent=False)),
    url(r'^w/', include('webapp.urls')),
    
    url(r'^accounts/signin/$', SigninV.as_view()),
    url(r'^accounts/signout/$', 'django.contrib.auth.views.logout'),
    url(r'^accounts/signup/$', SignupV.as_view()),

    url(r'^thirdparty/twitter/$', IndexV.as_view()),
    
    url(r'^thirdparty/twitter/authorize/$', 
        login_required(AuthorizeV.as_view())),
    url(r'^thirdparty/twitter/authorize_return/$', 
        login_required(AuthorizeReturnV.as_view())),
    url(r'^thirdparty/twitter/authorize_done/$', 
        login_required(AuthorizeDoneV.as_view())),
                       
    url(r'^eva/', include('eva.urls')),
                       
    #url(r'^', include('demo.urls')),
    #url(r'^thirdparty/twitter/signout/$', login_required(SignoutV.as_view())),
    
#    url(r'^thirdparty/twitter/authenticate/$', 
#        login_required(AuthenticateV.as_view()))

    
)