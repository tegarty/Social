from django.shortcuts import render,HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (ListView,DetailView,CreateView,
DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from braces.views import SelectRelatedMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Post
from groups.models import Group,GroupMember
from . import forms
# Create your views here.

User = get_user_model()

class PostListView(SelectRelatedMixin,ListView):
    model = Post
    select_related = ('user','group')

class UserPosts(ListView):
    model = Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
           self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        
        except User.DoesNotExist:
            raise Http404
        
        else:
            return self.post_user.posts.all()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context

class PostDetailView(SelectRelatedMixin,DetailView):
    model = Post
    select_related = ('user','group')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))

class CreatePostView(LoginRequiredMixin,SelectRelatedMixin,CreateView):
    model = Post
    form_class = forms.PostForm

    def form_valid(self,form):
        self.object = form.save(commit=False)
        user = self.request.user
        group = self.object.group
        isMember = GroupMember.objects.get(group=group,user=user)
        if isMember:
            self.object.user = user
            self.object.save()
            print(self.object.__dict__)
            print(self.object.user)

            return super().form_valid(form)
        else:
            return HttpResponseRedirect(reverse('posts:all'))


class DeletePostView(LoginRequiredMixin,SelectRelatedMixin,DeleteView):
    model = Post
    select_related = ('user','group')
    success_url = reverse_lazy('posts:all')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)
    
    def delete(self,*args,**kwargs):
        self.object = self.get_object()
        user = self.object.user
        group = self.object.group
        isMember = GroupMember.objects.get(group=group,user=user)
        if not isMember:
            return HttpResponseRedirect(self.success_url)
        messages.success(self.request,'Post Deleted')
        self.object.delete()
        return HttpResponseRedirect(self.success_url)
