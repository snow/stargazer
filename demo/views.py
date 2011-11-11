import urllib2
import json

from django.views.generic import View, TemplateView
from django.http import HttpResponse


class UnderConstructionView(TemplateView):
    template_name = 'demo/under_construction.html'

class IndexView(TemplateView):
    template_name = 'demo/index.html'

class CreatePostView(TemplateView):
    template_name = 'demo/post/create.html'
    
class LatLng2AddrView(View):
    API_URI = 'http://maps.googleapis.com/maps/api/geocode/json'
    
    API_RETRY_LIMIT = 3
    retry_count = 0
    
    def call_api(self, lat, lng):
        try:
            api_resp = urllib2.urlopen(self.API_URI+
                '?latlng={},{}&language=zh-CN&sensor=false'.format(lat, lng))
            
        except urllib2.URLError as err:
            if self.retry_count < self.API_RETRY_LIMIT:
                retry_count += 1
                return self.call_api(lat, lng)
            else:
                raise Exception('failed to connect Google Geocoding service')
        else:
            result = json.loads(api_resp.read())
    
            if 'OK' == result['status']:
                return result['results']
    
            # exceptions
            elif 'ZERO_RESULTS' == result['status'] or \
                 'NOT_FOUND' == result['status']:
                raise Exception('failed geocoding by Google Geocoding service')
            
            else:
                raise Exception('unregonized response from '+
                              'Google Geocoding service')
            
    def process_api_results(self, results):
        result = results[0]
    
        address = ''
        
        for com in result['address_components']:
            address = com['short_name'] + ' ' + address            
            if 'sublocality' in com['types']:
                break
        
        return address
    
    def get(self, request, *args, **kwargs):
        return HttpResponse(
            self.process_api_results(
                self.call_api(request.GET['lat'], request.GET['lng'])))