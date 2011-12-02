# Create your views here.
from django.views.generic import View, TemplateView, DetailView, RedirectView
from django.contrib.auth.models import User

from core.models import CreatePostForm

class DashboardV(TemplateView):
    template_name = 'webapp/dashboard.html'
    
class InitV(TemplateView):
    template_name = 'webapp/init.html'
    
class ListV(TemplateView):
    template_name = 'webapp/list.html'
    
class TeleportV(TemplateView):
    template_name = 'webapp/teleport.html'
    
class CreateV(TemplateView):
    '''Render an unbounded create post form'''
    template_name = 'webapp/post.html'
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = CreatePostForm()
        return self.render_to_response(context)
    
class SigninV(TemplateView):  
    '''Render a signin form which post to api'''
    template_name = 'webapp/signin.html'
    
class SignupV(TemplateView):  
    '''Render a signup form which post to api'''
    template_name = 'webapp/signup.html'
    
class MeV(RedirectView):
    permanent = False
    query_string = True

    def get(self, request, *args, **kwargs):
        self.url = '/w/user/{}/'.format(request.user.username)
        return super(MeV, self).get(request, *args, **kwargs)

class UserV(DetailView):
    model = User
    slug_field = 'username'
    template_name = 'webapp/user_profile.html'    