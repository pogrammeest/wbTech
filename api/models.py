import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse

from wbTech import settings


class Account(AbstractUser):
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    bio = models.TextField(default='no bio…', blank=True, max_length=3000)
    subs = models.ManyToManyField('self', related_name='my_subscriptions', symmetrical=False, blank=True, default=None,
                                  verbose_name='subscriptions')
    slug = models.SlugField(unique=True, blank=True)

    def get_absolute_url(self):
        return reverse("profiles:profile-detail", kwargs={"slug": self.slug})

    def get_posts(self):
        return self.posts.all()

    def get_posts_cnt(self):
        return self.posts.all().count()

    def get_subs(self):
        return Account.objects.filter(subs=self)

    def get_subs_cnt(self):
        return Account.objects.filter(subs=self).count()

    def get_subscriptions(self):
        return self.subs.all()

    def get_subscriptions_cnt(self):
        return self.subs.all().count()

    def get_all_authors_posts(self):
        return self.posts.all()

    def get_all_authors_posts_cnt(self):
        return self.posts.all().count()

    def get_liked_posts(self):
        return self.like_set.all()

    def get_liked_posts_cnt(self):
        return self.like_set.all().count()

    def get_likes_given_no(self):
        return self.like_set.all().count()

    def get_likes_recieved_no(self):
        return self.posts.all().annotate(liked_count=Count('liked'))[
            0].like_set.all().count() if self.posts.all().count() else 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.username) + '-' + str(uuid.uuid4())[:8].replace('-', ''))

        super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Post(models.Model):
    title = models.CharField(max_length=200, default='')
    content = models.TextField()
    liked = models.ManyToManyField(Account, blank=True, related_name='likes')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return str(f'{self.title} - {self.author.username}')

    def num_likes(self):
        return self.liked.all().count()

    def num_comments(self):
        return self.comment_set.all().count()

    class Meta:
        ordering = ('-created',)


class Comment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField(max_length=300)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)


class Like(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.post}"
