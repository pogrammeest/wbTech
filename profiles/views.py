from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import ProfileModelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required


@login_required
def my_profile_view(request):
    form = ProfileModelForm(request.POST or None, request.FILES or None, instance=request.user)
    updated = False
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            updated = True
    return render(request, 'profiles/my-profile.html', {'user': request.user, 'form': form, 'updated': updated})


@login_required
def profile_detail(request, slug):
    profile = get_object_or_404(Profile, slug__iexact=slug)
    if profile == request.user:
        return redirect('profiles:my-profile-view')

    return render(request, 'profiles/profile-detail.html', {'profile': profile})


@login_required
def subscribe_unsubscribe(request, slug):
    user = request.user
    if request.method == 'POST':
        profile = Profile.objects.get(id=request.POST.get('profile_id'))
        if profile in user.get_subscriptions():
            user.subs.remove(profile)
        else:
            user.subs.add(profile)
        user.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def profiles_list_view(request):
    profiles = Profile.objects.all()

    return render(request, 'profiles/profile-list.html', {'profiles': profiles})
