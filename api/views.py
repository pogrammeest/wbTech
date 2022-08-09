from django.utils.decorators import method_decorator
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .permissions import IsOwnerOrAdminAccount
from django.contrib.auth import authenticate
from .docs import *
from .models import *
from .serializers import *
from rest_framework import viewsets
from django.db.models import Q


@method_decorator(name="list", decorator=account_list)
@method_decorator(name="login", decorator=account_login)
class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be created, read, updated or deleted.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    http_method_names = ['get', 'post', 'head', 'put', 'delete']

    def list(self, request):
        """
        List of all profiles.
        """
        ordering = self.request.query_params.get('ordering', None)
        reverse = True if ordering == 'posts' else (False if ordering == '-posts' else None)

        serializer = AccountSerializer(Account.objects.all(), many=True, context={"request": request})

        if reverse is not None:
            return Response(sorted(serializer.data, key=lambda x: x['posts_count'], reverse=reverse))
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """
            Endpoint that give info about subscriptions, subscribers, posts and liked posts.
        """
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='related-info')
    def get_related_info(self, request, pk=None):
        """
            Endpoint that give info about subscriptions, subscribers, posts and liked posts.
        """
        profile = self.get_object()
        serializer = RelatedAccountInfoSerializer(profile, many=False, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='sub')
    def sub(self, request, pk=None):
        """
            Endpoint that allow to subscribe to user
        """
        user = request.user
        profile = self.get_object()

        if profile not in user.get_subscriptions():
            user.subs.add(profile)
            user.save()
            message = f'Successfully subscribed to user: {profile.username}.'
            sta = status.HTTP_200_OK
        else:
            message = f'You are already subscribed to user: {profile.username}.'
            sta = status.HTTP_400_BAD_REQUEST

        return Response({'message': message}, status=sta)

    @action(detail=True, methods=['get'], url_path='unsub')
    def unsub(self, request, pk=None):
        """
            Endpoint that allow to unsubscribe to user
        """
        user = request.user
        profile = self.get_object()

        if profile in user.get_subscriptions():
            user.subs.remove(profile)
            user.save()
            message = f'Successfully unsubscribed to user: {profile.username}.'
            sta = status.HTTP_200_OK
        else:
            message = f"You haven't subscribed to {profile.username} account yet."
            sta = status.HTTP_400_BAD_REQUEST
        return Response({'message': message}, status=sta)

    def get_permissions(self):
        if self.action in ['create', 'login']:
            permission = [permissions.AllowAny]
        elif self.action in ['update', 'delete']:
            permission = [IsOwnerOrAdminAccount]
        else:
            permission = [permissions.IsAuthenticated]
        return [permission() for permission in permission]


@method_decorator(name="create", decorator=post_swagger)
@method_decorator(name="update", decorator=post_swagger)
class PostViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows pro to be created, read, updated or deleted.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    http_method_names = ['get', 'post', 'head', 'put', 'delete']

    @action(detail=True, methods=['get'], url_path='like')
    def like(self, request, pk=None):
        """
            Endpoint that allow to like post
        """
        user = request.user
        post = self.get_object()
        if user not in post.liked.all():
            post.liked.add(user)

        like, created = Like.objects.get_or_create(user=user, post_id=post.pk)
        if not created:
            post.save()
            like.save()

        message = f'Successfully liked to post: {post.title}.'

        return Response({'message': message}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='unlike')
    def unlike(self, request, pk=None):
        """
            Endpoint that allow to unlike post
        """
        user = request.user
        post = self.get_object()
        if user in post.liked.all():
            post.liked.remove(user)
        like, created = Like.objects.get_or_create(user=user, post_id=post.pk)
        if not created:
            post.save()
            like.save()
        message = f'Successfully unliked to post: {post.title}.'
        return Response({'message': message}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='make-as-read')
    def make_as_read(self, request, pk=None):
        """
            Endpoint that allow to make post as read
        """
        user = request.user
        pk = int(pk)
        list_of_id = tuple(Post.objects.all().values_list('pk', flat=True))

        if pk not in list_of_id:
            return Response({'message': f'Post with id = {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        if pk not in user.already_seen_posts:
            user.already_seen_posts.append(pk)
            user.save()
            message = f'The post {pk} has been successfully marked as read.'
            sta = status.HTTP_200_OK
        else:
            message = f'Post {pk} already marked as read.'
            sta = status.HTTP_400_BAD_REQUEST
        return Response({'message': message}, status=sta)

    @action(detail=True, methods=['get'], url_path='make-as-unread')
    def make_as_unread(self, request, pk=None):
        """
            Endpoint that allow to make post as unread
        """
        pk = int(pk)
        list_of_id = tuple(Post.objects.all().values_list('pk', flat=True))
        user = request.user

        if pk not in list_of_id:
            return Response({'message': f'Post with id = {pk} not found.'}, status=status.HTTP_404_NOT_FOUND)
        if pk in user.already_seen_posts:
            user.already_seen_posts.remove(pk)
            user.save()
            message = f'The post {pk} has been successfully marked as unread.'
            sta = status.HTTP_200_OK
        else:
            message = f'Post {pk} already marked as unread.'
            sta = status.HTTP_400_BAD_REQUEST
        return Response({'message': message}, status=sta)

    def get_permissions(self):
        if self.action in ['update', 'delete']:
            permission = [IsOwnerOrAdminAccount]
        else:
            permission = [permissions.IsAuthenticated]
        return [permission() for permission in permission]


@method_decorator(name="list", decorator=feed_list)
class FeedViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allow you to get a feed from your subscriptions.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    def list(self, request):
        read_only = self.request.query_params.get('read_only', None)
        parametr = True if read_only == 'true' else None

        if parametr:
            q = Post.objects.filter(
                Q(author__in=request.user.subs.all()) & ~Q(pk__in=request.user.already_seen_posts)
            )
        else:
            q = Post.objects.filter(Q(author__in=request.user.subs.all()))
        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(q, request)
        serializer = PostSerializer(result_page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
