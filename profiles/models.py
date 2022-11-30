import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models import Count, Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from image_cropping import ImageRatioField, ImageCropField


class Profile(AbstractUser):
    class Role:
        ordinary_employee = "OE"
        head_of_department = "HOD"
        ROLE_CHOICES = (
            (ordinary_employee, "Рядовой сотрудник"),
            (head_of_department, "Руководитель подразделения"),
        )

    boss = models.ForeignKey(
        "self",
        related_name="slaves",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Начальник",
        default=None,

    )

    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    bio = models.TextField(default='no bio…', blank=True, max_length=3000)
    avatar = ImageCropField(default='img/avatars/avatar.png', upload_to='img/avatars/', blank=True)
    cropping = ImageRatioField('avatar', '250x250')
    subs = models.ManyToManyField('self', related_name='my_subscriptions', symmetrical=False, blank=True, default=None,
                                  verbose_name='subscriptions')
    slug = models.SlugField(unique=True, blank=True)

    role = models.CharField(
        "Роль", max_length=30, choices=Role.ROLE_CHOICES, default=Role.ordinary_employee
    )

    def clean(self):
        if not self._state.adding and self.role == Profile.Role.ordinary_employee and self.boss is None:
            raise ValidationError("У рядового сотрудника не может быть пустой начальник")

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
