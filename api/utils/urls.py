from django.conf.urls.defaults import patterns, include, url

from api.utils.views import *

urlpatterns = patterns('',
    url(r'^ll2a/$', LatLng2AddrView.as_view()),
)