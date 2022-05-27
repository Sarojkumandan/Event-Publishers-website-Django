from atexit import register
from distutils.command.upload import upload
from email.mime import image
from email.policy import default
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse

class User(AbstractUser):
    is_user = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)


class Post(models.Model):
    event_name = models.CharField(max_length=100)
    image_link = models.CharField(max_length=2000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=250)
    event_date = models.CharField(max_length=100)
    register_link = models.CharField(max_length=2000, null=True, blank=True)
    long = models.FloatField(null=True, blank=True)
    lang = models.FloatField(null=True, blank=True)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes',blank=True)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)

    def __str__(self):
        return self.event_name

    def get_absolute_url(self):
        return reverse('post-detail',kwargs={'pk':self.pk})
