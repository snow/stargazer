from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

from api.accounts.views import *

urlpatterns = patterns('',
    url(r'^signin.(?P<format>json|html)$', SigninV.as_view()),
)