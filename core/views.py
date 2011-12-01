# -*- coding: UTF-8 -*-
import logging

from django.http import HttpResponseRedirect
from django.views.generic import View

l = logging.getLogger(__name__)

class SigninV(View):
    '''Redirect mobile visitor to mobile signin'''
    
    def get(self, request, *args, **kwargs):
        '''redirect to coresponding uri to show singin form'''
        go_to = request.GET.get('next', '')
        if go_to.startswith('/w/'):
            return HttpResponseRedirect('/w/signin/?'+request.GET.urlencode())
        else:
            raise Exception('not yet implemented signin for non-mobile')