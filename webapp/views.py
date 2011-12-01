# Create your views here.
from django.views.generic import View, TemplateView, RedirectView

from core.models import CreatePostForm

class IndexV(TemplateView):
    template_name = 'webapp/index.html'
    
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