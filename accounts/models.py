from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy
from django.conf import settings


def pic_upload(instance, filename):
    return f"images/{instance.username}/{filename}"


def resumes_upload(instance, filename):
    return f"files/{instance.username}/{filename}"


# Create your models here.
class Ability(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Following(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='followings'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.follower.username

    def get_absolute_url(self):
        return reverse_lazy('accounts:user', username=self.follower.username)



class User(AbstractUser):
    photo = models.ImageField(upload_to=pic_upload)
    about = models.TextField(max_length=200)
    is_author = models.BooleanField(default=False)
    intro_url = models.URLField()
    resume = models.FileField(upload_to=resumes_upload)
    abilities = models.ManyToManyField(Ability)
    # verified = models.BooleanField(default=False)
    # archived = models.BooleanField(default=False)
    # secondary_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse_lazy('accounts:user', username=self.username)

    def is_premium(self):
        if self.premium_plans.all():
            return True
        return False
