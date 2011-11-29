# Create your views here.
import json

from django.views.generic import View
from django.http import HttpResponse

from core.utils import LatLng2Addr

class LatLng2AddrView(View):
    '''reverse geocoding given latitude and longitude into address'''

    def post(self, request, *args, **kwargs):
        latlng2addr = LatLng2Addr()
        try:
            addr = latlng2addr.get(request.POST['lat'], request.POST['lng'])
            err = False
            status = 200
        except LatLng2Addr.BaseException as e:
            addr = ''
            err = e.message
            status = 500
            
        return HttpResponse(json.dumps({
                                'error': err,
                                'addr': addr,
                            }),
                            content_type='application/json',
                            status=status)