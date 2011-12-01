# Create your views here.
import json

from django.views.generic import View, ListView, CreateView
from django.http import HttpResponse

from core.models import Post, CreatePostForm, Author

class ListV(ListView):
    '''Return posts by geo'''
    template_name = 'api/posts/stream_content.html'
    
    def get(self, request, lat, lng, type, format, *args, **kwargs):
        '''TODO'''
        mgr = Post.objects.nearby(float(lat), float(lng))
        if request.user.is_authenticated():
            mgr.with_user(request.user)                
        
        if 'recent' == type:
            self.queryset = mgr.recent().all()
        elif 'trending' == type:
            self.queryset = mgr.trending().all()
        elif 'top' == type:
            self.queryset = mgr.top().all()
            
        if 'json' == format:
            pass
#            return HttpResponse(json.dumps({
#                                    'results': True
#                                }),
#                                content_type='application/json')
        elif 'html' == format:
            return super(ListV, self).get(request, *args, **kwargs)
        else:
            # raise exception?
            pass
        

class ListByUserV(View):
    '''Return posts by user'''
    
    
class ShowV(View):
    '''Return properties of a post'''  
    
class CreateV(CreateView):
    '''Create a post'''
    form_class = CreatePostForm
    #template_name = 'demo/post/create.html'

    def form_valid(self, form):
        post = form.instance
        user = self.request.user
        
        try:
            author = user.author_set.filter(source=Author.T_LOCAL).get()
        except Author.DoesNotExist:
            author = Author(name=user.username, source=Author.T_LOCAL,
                            owner=user)
            author.save()

        post.author = author
        post.save()
        
        if self.request.POST['return']:
            success_url = self.request.POST['return'] + 'lat{}/lng{}/recent/'
                
        return HttpResponse(json.dumps({
                                'done': True,
                                'post_id': post.id,
                                'go_to': success_url.format(post.latitude, 
                                                            post.longitude)
                            }),
                            content_type='application/json')
    
    def form_invalid(self, form):
        '''TODO'''
        raise
    
class LikeV(View):
    '''Toggle "like" of a post'''
    def post(self, request, id):
        post = Post.objects.get(pk=id)
        if 0 == post.likes.filter(id=request.user.id).count():
            post.likes.add(request.user)
            act = 'added'
        else:
            post.likes.remove(request.user)
            act = 'removed'

        return HttpResponse(json.dumps({
                                'done': True,
                                'act': act,
                            }),
                            content_type='application/json')
        
class BanV(View):
    '''Toggle "ban" of a post'''
    def post(self, request, id):
        post = Post.objects.get(pk=id)
        if 0 == post.bans.filter(id=request.user.id).count():
            post.bans.add(request.user)
            act = 'added'
        else:
            post.bans.remove(request.user)
            act = 'removed'

        return HttpResponse(json.dumps({
                                'done': True,
                                'act': act,
                            }),
                            content_type='application/json')        