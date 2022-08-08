import uuid
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models import Count
from django.template.defaultfilters import slugify
from django.urls import reverse
from image_cropping import ImageRatioField, ImageCropField


class Profile(AbstractUser):
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    bio = models.TextField(default='no bio…', blank=True, max_length=3000)
    avatar = ImageCropField(default='img/avatars/avatar.png', upload_to='img/avatars/', blank=True)  # image cropping
    cropping = ImageRatioField('avatar', '250x250')
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
        return Profile.objects.filter(subs=self)

    def get_subs_cnt(self):
        return Profile.objects.filter(subs=self).count()

    def get_subscriptions(self):
        return self.subs.all()

    def get_subscriptions_cnt(self):
        return self.subs.all().count()

    def get_all_authors_posts(self):
        return self.posts.all().count()

    def liked_posts(self):
        return self.like_set.all()

    def liked_posts_cnt(self):
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
