from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from eva.views import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', login_required(IndexV.as_view())),
)