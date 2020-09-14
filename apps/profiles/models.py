from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    A User Profile
    """
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    guid = models.CharField(max_length=100, null=True, unique=True)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile for every users
    """
    if created:
        Profile.objects.create(user=instance)
