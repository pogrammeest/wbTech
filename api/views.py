from django.shortcuts import render
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .permissions import IsOwnerOrAdmin, IsOwnerOrAdminProfile

from profiles.models import Profile
from posts.models import Post
from .serializers import *
from django_filters import rest_framework
from rest_framework import viewsets, filters
from django.db import connection


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def list(self, request):
        ordering = self.request.query_params.get('ordering', None)
        reverse = True if ordering == 'posts' else (False if ordering == '-posts' else None)

        serializer = ProfileSerializer(Profile.objects.all(), many=True, context={"request": request})

        if reverse is not None:
            return Response(sorted(serializer.data, key=lambda x: x['posts_count'], reverse=reverse))
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='related-info')
    def get_related_info(self, request, pk=None):
        profile = self.get_object()
        serializer = RelatedProfileInfoSerializer(profile, many=False, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'get'], url_path='sub-unsub')
    def sub_unsub(self, request, pk=None):
        user = request.user
        profile = self.get_object()

        if profile in user.get_subscriptions():
            user.subs.remove(profile)
            message = f'Successfully unsubscribed to user: {profile.username}.'
        else:
            user.subs.add(profile)
            message = f'Successfully subscribed to user: {profile.username}.'
        user.save()
        return Response({'message': message}, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'create':
            permission = [permissions.AllowAny]
        elif self.action in ['update']:
            permission = [IsOwnerOrAdminProfile]
        else:
            permission = [permissions.IsAuthenticated]
        return [permission() for permission in permission]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action == 'update':
            permission = [IsOwnerOrAdminProfile]
        else:
            permission = [permissions.IsAuthenticated]
        return [permission() for permission in permission]


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination

    def list(self, request):
        cursor = connection.cursor()
        q = Post.objects.filter(author__in=request.user.subs.all())
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(q, request)

        serializer = PostSerializer(result_page, many=True, context={"request": request})

        return paginator.get_paginated_response(serializer.data)
