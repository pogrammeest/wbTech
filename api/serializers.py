from rest_framework import serializers
from profiles.models import *
from posts.models import *
import re

class RelatedProfileInfoSerializer(serializers.HyperlinkedModelSerializer):
    subscriptions = serializers.SerializerMethodField()
    subscribers = serializers.SerializerMethodField()
    posts = serializers.HyperlinkedRelatedField(read_only=True, required=False, many=True, view_name='api:post-detail')
    liked_posts = serializers.SerializerMethodField()

    def get_liked_posts(self, obj):
        return [self.context.get('request').build_absolute_uri(f'/api/post/{inst.post.pk}/') for inst in
                obj.liked_posts()]

    def get_sub_mixin(self, func):
        return [self.context.get('request').build_absolute_uri(f'/api/profile/{inst.pk}/') for inst in func()]

    def get_subscriptions(self, obj):
        return self.get_sub_mixin(obj.get_subscriptions)

    def get_subscribers(self, obj):
        return self.get_sub_mixin(obj.get_subs)

    class Meta:
        model = Profile
        fields = ['subscriptions', 'subscribers', 'posts', 'liked_posts']
        read_only_fields = ['subscriptions', 'subscribers', 'posts', 'liked_posts']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    """Profiles"""
    id = serializers.HyperlinkedIdentityField(view_name="api:profile-detail")
    avatar_url = serializers.SerializerMethodField()

    '''actions'''
    # sub_unsub = serializers.HyperlinkedIdentityField(view_name='api:profile-sub-unsub', read_only=True)
    # related_info = serializers.HyperlinkedIdentityField(view_name='api:related-info', read_only=True)

    '''calculated field'''
    subscriptions_count = serializers.SerializerMethodField(source='get_posts_cnt')
    subscribers_count = serializers.SerializerMethodField()
    liked_posts_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField(source='')

    def get_subscriptions_count(self, obj):
        return obj.get_subscriptions_cnt()

    def get_subscribers_count(self, obj):
        return obj.get_subs_cnt()

    def get_liked_posts_count(self, obj):
        return obj.liked_posts_cnt()

    def get_posts_count(self, obj):
        return obj.get_posts_cnt()

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.avatar.url)

    def create(self, validated_data):
        user = super(ProfileSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        user = super(ProfileSerializer, self).update(instance, validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    class Meta:
        model = Profile
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'password', 'avatar_url', 'bio', 'slug',
                  'is_staff', 'subscriptions_count', 'subscribers_count', 'liked_posts_count',
                  'posts_count']
        read_only_fields = (
            'id', 'is_staff', 'avatar_url', 'subscriptions_count', 'subscribers_count',
            'liked_posts_count',
            'posts_count')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def __init__(self, *args, **kwargs):
        super(ProfileSerializer, self).__init__(*args, **kwargs)
        if 'request' in self.context and re.search('/api/profile/[0-9]*/', self.context['request'].META['PATH_INFO']):
            self.fields['id'] = serializers.IntegerField()


class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = ProfileSerializer(many=False, read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    id = serializers.HyperlinkedIdentityField(view_name="api:post-detail")

    def get_validation_exclusions(self):
        exclusions = super(PostSerializer, self).get_validation_exclusions()
        return exclusions + ['author']

    def create(self, validated_data):
        user = self.context.get('request').user
        if 'author_id' in validated_data and not user.is_staff:
            raise serializers.ValidationError(
                {'code': 400, 'message': "Validation Failed! You don't have enough rights for this operation."})

        validated_data['author'] = user
        post = super(PostSerializer, self).create(validated_data)
        return post

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'updated', 'created', 'author', 'author_id']
        read_only_fields = ('id', 'author')
        extra_kwargs = {
            'author_id': {'write_only': True}
        }
