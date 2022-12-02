from django.db import models

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser

from django.utils import timezone
# Create your models here.
from django.utils.translation import gettext as _

class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(_('Users must have an username'))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)



class User(AbstractBaseUser, PermissionsMixin):

    Bs_1 = 'Bachelor 1st'
    Bs_2 = 'Bachelor 2nd'
    Bs_3 = 'Bachelor 3rd'
    Bs_4 = 'Bachelor 4th'
    Ms_1 = 'Master 1st'
    Ms_2 = 'Master 2nd'
    Phd = 'Phd'

    CHOICES = (
        (Bs_1, 'Bachelor 1st'),
        (Bs_2, 'Bachelor 2nd'),
        (Bs_3, 'Bachelor 3rd'),
        (Bs_4, 'Bachelor 4th'),
        (Ms_1, 'Master 1st'),
        (Ms_2, 'Master 2nd'),
        (Phd, 'Phd')
    )

    INTERNATIONAL = "International"
    CIS = "CIS"
    RUSSIAN = "Russian"

    LOCATIONS = (
        (INTERNATIONAL, 'International'),
        (CIS, "CIS"),
        (RUSSIAN, "Russian")
    )

    username = models.CharField(max_length=50, unique=True)
    telegram_username = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(max_length=250, unique=True, null=True, blank=True)
    inno_email = models.EmailField(max_length=250, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    telegram_first_name = models.CharField(max_length=30, blank=True, null=True)
    telegram_last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    receive_notification = models.BooleanField(default=True)
    course = models.CharField(max_length=20, choices=CHOICES, null=True, blank=True)
    group = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=50, choices=LOCATIONS, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self) -> str:
        return self.username




class Conversation(models.Model):
    users = models.ManyToManyField(User, related_name='conversations')
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-modified_at']

    
class ConversationMessage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        self.conversation.save()

        super(ConversationMessage, self).save(*args, **kwargs)




class Notification(models.Model):

    MESSAGE = 'message'
    NEW_JOIN = 'new_join'


    CHOICES = (
        (MESSAGE, 'Message'),
        (NEW_JOIN, 'New_Join')
    )


    to_user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=CHOICES)

    created_by = models.ForeignKey(User, related_name='creatednotifications', on_delete=models.CASCADE)
    class Meta:
        ordering = ['-created_at']
