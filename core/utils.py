# -*- coding: UTF-8 -*-
import urllib2
import json

from django.conf import settings

class LatLng2Addr():
    API_URI = 'http://maps.googleapis.com/maps/api/geocode/json'
    API_RETRY_LIMIT = 3
    TIMES_OVER_QUERY_ALLOWED = 10
    TIMES_TOTAL_QUERY_ALLOWED = 2000
    
    def __init__(self):
        self.retry_count = 0
        self.times_over_limit = 0
        self.times_total_query = 0
    
    class BaseException(Exception):
        message = 'failed to get address from latlng'
    
    class ConnectionFailed(BaseException):
        message = 'failed to connect Google Geocoding service'
    
    class GeocodingFailed(BaseException):
        message = 'failed geocoding by Google Geocoding service'
    
    class OverQueryLimit(BaseException):
        message = 'over query limit of Google Geocoding service'
        
    class RequestDenied(BaseException):
        message = 'request denied by Google Geocoding service'
    
    class UnregonizedResponse(BaseException):
        message = 'unregonized response from Google Geocoding service'
        
        def __init__(self, status, *args, **kwargs):
            self.message += ': ' + status
            super(LatLng2Addr.UnregonizedResponse, self).__init__(*args, 
                                                                  **kwargs)

    def call_api(self, lat, lng):
        '''TODO'''
        
        if self.TIMES_TOTAL_QUERY_ALLOWED <= self.times_total_query:
            raise self.OverQueryLimit()
        
        try:
            api_resp = urllib2.urlopen(self.API_URI+
                '?latlng={},{}&language=zh-CN&sensor=false'.format(lat, lng))

        except urllib2.URLError as err:
            if self.retry_count < self.API_RETRY_LIMIT:
                retry_count += 1
                return self.call_api(lat, lng)
            else:
                raise self.ConnectionFailed()
        else:
            result = json.loads(api_resp.read())
            
            self.times_total_query += 1

            if 'OK' == result['status']:
                return result['results']

            # exceptions
            elif 'ZERO_RESULTS' == result['status'] or \
                 'NOT_FOUND' == result['status']:
                raise self.GeocodingFailed()
                
            elif 'OVER_QUERY_LIMIT' == result['status']:
                self.times_over_limit += 1
                if self.TIMES_OVER_QUERY_ALLOWED <= self.times_over_limit:
                    raise self.OverQueryLimit()
                else:
                    raise self.ConnectionFailed()
            
            elif 'REQUEST_DENIED' == result['status']:
                raise self.RequestDenied()

            else:
                raise self.UnregonizedResponse(result['status'])

    def process_api_results(self, results):
        result = results[0]
        address = ''

        for com in result['address_components']:
            address = com['short_name'] + ' ' + address
            if 'sublocality' in com['types']:
                break

        return address.strip()
    
    def get(self, lat, lng):
        return self.process_api_results(self.call_api(lat, lng))