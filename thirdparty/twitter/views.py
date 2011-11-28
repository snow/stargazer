#from django.views.generic import View
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from tweepy import OAuthHandler, API

AUTHORIZE_START_URI = '/thirdparty/twitter/authorize/'
AUTHORIZE_RETURN_URI = '/thirdparty/twitter/authorize_return/'
AUTHORIZE_DONE_URI = '/thirdparty/twitter/authorize_done/'

class BaseOAuthV(View):
    '''Base class for all views that will use OAuth handler'''
    def __init__(self, *args, **kwargs):
        self.oauth = OAuthHandler(settings.TWITTER_CONSUMER_KEY,
                                  settings.TWITTER_CONSUMER_SECRET,
                                  secure=True)
        super(BaseOAuthV, self).__init__(*args, **kwargs)
    
class IndexV(BaseOAuthV):    
    '''Index, determine what action should take'''
    def get(self, request):
        if request.user.is_authenticated():        
            profile = request.user.get_profile()
            
            if profile.twitter_key:
                return HttpResponseRedirect(AUTHORIZE_DONE_URI)
            else:
                return HttpResponseRedirect(AUTHORIZE_START_URI)
        else:
            # show signin with twitter page
            pass
        
class AuthorizeV(BaseOAuthV):        
    '''Start from here. Redirect to twitter authorizing page'''    
    def get(self, request):
        self.oauth.callback = request.build_absolute_uri(AUTHORIZE_RETURN_URI)
        redirect_to = self.oauth.get_authorization_url()
        # request token could being get after get_authorization_url()
        request.session['unauthed_token'] = self.oauth.request_token
        return HttpResponseRedirect(redirect_to)
    
class AuthorizeReturnV(BaseOAuthV):        
    '''Twitter redirect user to here after authorize'''    
    def get(self, request):
        if request.session['unauthed_token'].key == request.GET['oauth_token']:
            self.oauth.set_request_token(request.GET['oauth_token'], 
                                         settings.TWITTER_CONSUMER_SECRET)
            access_token = self.oauth.get_access_token(
                                request.GET['oauth_verifier'])
        else:
            raise Exception('token not match, something went wrong')
        
        twitter_user = API(auth_handler=self.oauth).verify_credentials()
        
        profile = request.user.get_profile()
        profile.twitter_id = twitter_user.id
        profile.twitter_username = twitter_user.screen_name
        profile.twitter_key = access_token.key
        profile.twitter_secret = access_token.secret
        profile.save()
        
        return HttpResponseRedirect(AUTHORIZE_DONE_URI)
    
class AuthorizeDoneV(BaseOAuthV):
    '''TODO'''
    def get(self, request):
        up = request.user.get_profile()
        
        self.oauth.set_access_token(up.twitter_key, up.twitter_secret)
        twittter_user = API(auth_handler=self.oauth).verify_credentials()
        
        return HttpResponse('connected with {} {}'.\
                                format(twittter_user.id, 
                                       twittter_user.screen_name))
    
#class AuthenticateV(BaseOAuthV):        
#    '''View for path/to/3rdparty/twitter/authenticate'''
#    def get(self, request):        
#        pass
    
#class SignoutV(BaseOAuthV):
#    '''/to/thirdparty/twitter/signout/'''
#    def get(self, request, *args, **kwargs):
#        request.session.flush()
#        return HttpResponseRedirect('/')
        