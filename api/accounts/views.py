# Create your views here.
import json
import urlparse

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, \
                                login as auth_login
from django.contrib.auth.forms import AuthenticationForm
#from django.contrib.auth.views import login

from core.models import UserCreationForm

def _clean_redirect_uri(redirect_to, request):
    netloc = urlparse.urlparse(redirect_to)[1]
    
    # Use default setting if redirect_to is empty
    if not redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL

    # Security check -- don't allow redirection to a different
    # host.
    elif netloc and netloc != request.get_host():
        redirect_to = settings.LOGIN_REDIRECT_URL
        
    return redirect_to
    
class SigninV(View):
    '''Signin'''
    def post(self, request, format):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Okay, security checks complete. Log the user in.
            # authenticate() called in AuthenticationForm
            auth_login(request, form.get_user())
            
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                
            redirect_to = _clean_redirect_uri(
                                request.REQUEST.get('next', ''), 
                                request)
                
            if 'json' == format:
                return HttpResponse(json.dumps({
                                        'done': True,
                                        'user_id': form.get_user().id,
                                        'is_signedin': True,
                                        'go_to': redirect_to
                                    }),
                                    content_type='application/json')
            elif 'html' == format:
                return HttpResponseRedirect(redirect_to)
        else:
            if 'json' == format:
                return HttpResponse(json.dumps({
                                        'done': False,
                                        'errors': form.errors
                                    }),
                                    content_type='application/json',
                                    status=500)
            elif 'html' == format:
                return HttpResponse(form.errors.as_ul(), status=500)


class SignupV(View):
    '''Signup'''
    def post(self, request, format):
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
            if user is not None:
                auth_login(request, user)
                
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                    
                redirect_to = _clean_redirect_uri(
                                    request.REQUEST.get('next', ''), 
                                    request)
                    
                if 'json' == format:
                    return HttpResponse(json.dumps({
                                            'done': True,
                                            'user_id': user.id,
                                            'is_signedin': True,
                                            'go_to': redirect_to
                                        }),
                                        content_type='application/json')
                elif 'html' == format:
                    return HttpResponseRedirect(redirect_to)
            else:
                raise Exception('failed to auth newly-created user')
        else:
            if 'json' == format:
                return HttpResponse(json.dumps({
                                        'done': False,
                                        'errors': form.errors
                                    }),
                                    content_type='application/json',
                                    status=500)
            elif 'html' == format:
                return HttpResponse(form.errors.as_ul(), status=500)
