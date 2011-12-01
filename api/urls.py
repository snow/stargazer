from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'utils/', include('api.utils.urls')),
    url(r'posts/', include('api.posts.urls')),
    url(r'users/', include('api.users.urls')),
    url(r'accounts/', include('api.accounts.urls')),
)