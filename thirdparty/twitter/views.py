#from django.views.generic import View
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from tweepy import OAuthHandler

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
        redirect_to = self.oauth_handler.get_authorization_url()
        request.session['unauthed_token'] = self.oauth_handler.request_token
        return HttpResponseRedirect(redirect_to)
    
class AuthorizeReturnV(BaseOAuthV):        
    '''View for path/to/3rdparty/twitter/authorize_return'''    
    def get(self, request):        
        return HttpResponse('meow~')
    
class AuthenticateV(BaseOAuthV):        
    '''View for path/to/3rdparty/twitter/authenticate'''
    def get(self, request):        
        pass
        