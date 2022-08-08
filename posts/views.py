from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import *
from .forms import *
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection


def post_mixin(request, only_feed: bool):
    user = request.user
    if only_feed:
        cursor = connection.cursor()
        cursor.execute(
            f'''select * from posts_post post join profiles_profile_subs on to_profile_id = post.author_id where from_profile_id = {request.user.pk}''')
        current_id = [obj[0] for obj in cursor.fetchall()]
        posts = Post.objects.filter(pk__in=current_id)
    else:
        posts = Post.objects.all()
    post_form = PostModelForm()
    comment_form = CommentModelForm()
    post_added = False

    if 'submit_post_form' in request.POST:
        post_form = PostModelForm(request.POST, request.FILES)
        if post_form.is_valid():
            ins = post_form.save(commit=False)
            ins.author = user
            ins.save()
            post_added = True
            # return redirect(request.META.get('HTTP_REFERER'), {'post_added':True})

    if 'submit_comment_form' in request.POST:
        comment_form = CommentModelForm(request.POST or None)
        if comment_form.is_valid():
            ins = comment_form.save(commit=False)
            ins.user = user
            ins.post = Post.objects.get(id=request.POST.get('post_id'))
            ins.save()
            print(request.META)
            print(request.path)
            return redirect(request.META.get('HTTP_REFERER'))

    return render(request, 'posts/main.html',
                  {'posts': posts, 'post_form': post_form, 'comment_form': comment_form, 'post_added': post_added,
                   'user': user})


@login_required
def post_comment_create_and_list_view_feed(request):
    return post_mixin(request, True)


@login_required
def post_comment_create_and_list_view_all(request):
    return post_mixin(request, False)


@login_required
def like_unlike(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)

        if user in post_obj.liked.all():
            post_obj.liked.remove(user)
        else:
            post_obj.liked.add(user)

        like, created = Like.objects.get_or_create(user=user, post_id=post_id)
        if not created:
            post_obj.save()
            like.save()

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def post_detail(request, pk):
    comment_form = CommentModelForm()
    post = get_object_or_404(Post, pk__iexact=pk)

    return render(request, 'posts/post-detail.html', {'post': post, 'comment_form': comment_form})


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/confirm_del.html'
    success_url = reverse_lazy('posts:all-post-view')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        post = Post.objects.get(pk=pk)
        if not post.author == self.request.user:
            messages.waring(self.request, 'Authentication error')
        return post


class PostUpdateView(UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'posts/update.html'
    success_url = reverse_lazy('posts:all-post-view')

    def form_valid(self, form):
        user = self.request.user
        if form.instance.author == user:
            return super().form_valid(form)
        form.add_error(None, 'Authentication error')
        return super().form_invalid(form)
