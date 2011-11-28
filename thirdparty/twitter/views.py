#from django.views.generic import View
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from tweepy import OAuthHandler as tweepy_OAuthHandler, TweepError, oauth

import pprint

from urllib2 import Request, urlopen
import base64

from tweepy.api import API

pp = pprint.PrettyPrinter(indent=4)

class OAuthHandler(tweepy_OAuthHandler):
    '''TODO'''
#    def get_authorization_url(self, signin_with_twitter=False):
#        """Get the authorization URL to redirect the user"""
#        try:
#            # get the request token
#            self.request_token = self._get_request_token()
#
#            # build auth request and return as url
#            if signin_with_twitter:
#                url = self._get_oauth_url('authenticate')
#            else:
#                url = self._get_oauth_url('authorize')
#            request = oauth.OAuthRequest.from_token_and_callback(
#                token=self.request_token, 
#                http_url=url,
#                callback=self.callback
#            )
#
#            return request.to_url()
#        except Exception, e:
#            raise #TweepError(e)
#        
#    def _get_request_token(self):
#        try:
#            url = self._get_oauth_url('request_token')
#            request = oauth.OAuthRequest.from_consumer_and_token(
#                self._consumer, http_url=url, callback=self.callback
#            )
#            request.sign_request(self._sigmethod, self._consumer, None)
#            
#            return request.to_url()
#            
#            resp = urlopen(Request(url, headers=request.to_header()))
#            return oauth.OAuthToken.from_string(resp.read())
#        except Exception, e:
#            raise #TweepError(e)

class BaseOAuthV(View):
    '''TODO'''
    
    def __init__(self, *args, **kwargs):
        self.oauth_handler = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                          settings.TWITTER_CONSUMER_SECRET,
                                          secure=True)
        super(BaseOAuthV, self).__init__(*args, **kwargs)
    
    
class IndexV(BaseOAuthV):    
    '''View for path/to/3rdparty/twitter/ '''
    def get(self, request):
        access_token = request.session.get('access_token', None)
        if not access_token:
            return HttpResponseRedirect('/thirdparty/twitter/authorize/')
        
class AuthorizeV(BaseOAuthV):        
    '''View for path/to/3rdparty/twitter/authorize'''    
    def get(self, request):
        self.oauth_handler.callback = request.build_absolute_uri(
                                        '/thirdparty/twitter/authorize_return/')
        redirect_to = self.oauth_handler.get_authorization_url()
        request.session['unauthed_token'] = self.oauth_handler.request_token
        return HttpResponseRedirect(redirect_to)
        #return HttpResponse(request_token)
    
class AuthorizeReturnV(BaseOAuthV):        
    '''View for path/to/3rdparty/twitter/authorize_return'''    
    def get(self, request):
        if request.session['unauthed_token'].key == request.GET['oauth_token']:
            self.oauth_handler.set_request_token(request.GET['oauth_token'], 
                                                 settings.TWITTER_CONSUMER_SECRET)
            self.oauth_handler.get_access_token(request.GET['oauth_verifier'])
        
        api = API(auth_handler=self.oauth_handler)
        user = api.verify_credentials()
        return HttpResponse(user.name)
    
class AuthenticateV(BaseOAuthV):        
    '''View for path/to/3rdparty/twitter/authenticate'''
    def get(self, request):        
        pass
    
class SignoutV(BaseOAuthV):
    '''/to/thirdparty/twitter/signout/'''
    def get(self, request, *args, **kwargs):
        request.session.flush()
        return HttpResponseRedirect('/')    
        