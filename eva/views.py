# Create your views here.
from django.views.generic import TemplateView

class IndexV(TemplateView):
    template_name = 'eva/index.html'