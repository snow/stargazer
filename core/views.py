# Create your views here.
import json

from django.views.generic import View
from django.http import HttpResponse

from core.utils import LatLng2Addr

class LatLng2AddrView(View):
    '''TODO'''

    def post(self, request, *args, **kwargs):
        latlng2addr = LatLng2Addr()
        try:
            addr = latlng2addr.get(request.POST['lat'], request.POST['lng'])
            err = False
        except LatLng2Addr.BaseException as e:
            addr = ''
            err = e.message
            
        return HttpResponse(json.dumps({
                                'error': err,
                                'addr': addr,
                            }),
                            content_type='application/json')