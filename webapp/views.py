# Create your views here.
from django.views.generic import View, TemplateView, RedirectView

class IndexV(TemplateView):
    template_name = 'webapp/index.html'
    
class ListV(TemplateView):
    template_name = 'webapp/list.html'
    
class TeleportV(TemplateView):
    template_name = 'webapp/teleport.html'