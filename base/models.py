from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)
    
    avatar = models.ImageField(null=True, default="avatar.svg")

    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['']

    #my code starts
    REQUIRED_FIELDS = ['username']  # Add 'username' to REQUIRED_FIELDS

    def save(self, *args, **kwargs):
        # Set the 'username' field to the 'email' value if it is not provided
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
    #my code ends


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    private=models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['updated', 'created']

    def __str__(self):
        return self.body[0:50]

class Follow(models.Model):
    followed=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    followers = models.ManyToManyField(
        User, related_name='followers', blank=True)
    

class JoinRequest(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='join_requests')
    applicant=models.ForeignKey(User, on_delete=models.CASCADE)
    approveStatus=models.BooleanField(default=False)


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['updated', 'created']

    def __str__(self):
        return self.body[0:50]
