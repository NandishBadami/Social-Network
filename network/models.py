from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
class Follower(models.Model):
    leader = models.ForeignKey(User, related_name='leader', blank=True, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='follower', blank=True, on_delete=models.CASCADE)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    like = models.IntegerField()