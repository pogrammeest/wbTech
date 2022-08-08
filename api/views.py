from django.shortcuts import render
from django.utils.decorators import method_decorator
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


@method_decorator(name="list", decorator=swagger_auto_schema(manual_parameters=[
    openapi.Parameter("ordering",
                      openapi.IN_QUERY,
                      description="Source reference",
                      type=openapi.TYPE_STRING, enum=['posts', '-posts']
                      )
]))
class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be created, read, updated or deleted.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ['get', 'post', 'head', 'put', 'delete']

    def list(self, request):
        """
        List of all profiles.
        """
        ordering = self.request.query_params.get('ordering', None)
        reverse = True if ordering == 'posts' else (False if ordering == '-posts' else None)

        serializer = ProfileSerializer(Profile.objects.all(), many=True, context={"request": request})

        if reverse is not None:
            return Response(sorted(serializer.data, key=lambda x: x['posts_count'], reverse=reverse))
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='related-info')
    def get_related_info(self, request, pk=None):
        """
            Endpoint that give info about subscriptions, subscribers, posts and liked posts.
        """
        profile = self.get_object()
        serializer = RelatedProfileInfoSerializer(profile, many=False, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='sub-unsub')
    def sub_unsub(self, request, pk=None):
        """
            Endpoint that allow to subscribe and unsubscribe
        """
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


post_swagger = swagger_auto_schema(request_body=openapi.Schema(
    title=("Create post"),
    type=openapi.TYPE_OBJECT,
    required=['title', 'content'],
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING, description=('Title of post'), example=('string'),
                                title='Title'
                                ),
        'content': openapi.Schema(type=openapi.TYPE_STRING, description=('Content of post'),
                                  example=('string'), title='Content'),
        'author_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                    description=('Author id, available only for staff user'),
                                    example=(1), title='Author id'),
    }
)
)


@method_decorator(name="create", decorator=post_swagger)
@method_decorator(name="update", decorator=post_swagger)
class PostViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows pro to be created, read, updated or deleted.
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names = ['get', 'post', 'head', 'put', 'delete']

    def create(self, request):
        return super(PostViewSet, self).create(request)

    def update(self, request, pk=None):
        return super(PostViewSet, self).update(request, pk)

    def get_permissions(self):
        if self.action == 'update':
            permission = [IsOwnerOrAdminProfile]
        else:
            permission = [permissions.IsAuthenticated]
        return [permission() for permission in permission]


class FeedViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allow you to get a feed from your subscriptions.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get']

    def list(self, request):
        q = Post.objects.filter(author__in=request.user.subs.all())
        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(q, request)
        serializer = PostSerializer(result_page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
