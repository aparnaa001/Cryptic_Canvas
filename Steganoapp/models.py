from django.db import models
from django.contrib.auth.models import User
# Create your models here.



class Registeration(models.Model):
    name = models.CharField(max_length=50,null=True)
    number = models.CharField(max_length=25,null=True)
    mail = models.EmailField(null=True)
    age = models.IntegerField(null=True)
    image = models.ImageField(null=True)
    joined = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)

class Userhistory(models.Model):
    user = models.ForeignKey(Registeration,on_delete=models.CASCADE,null=True)
    stegoimage = models.ImageField(null=True)
    date = models.DateTimeField(auto_now_add=True)

class Decrypt(models.Model):
    image=models.ImageField(null=True)

class Feedback(models.Model):
    feedback=models.CharField(max_length=500,null=True)
    star=models.IntegerField(null=True)
    user=models.ForeignKey(Registeration,on_delete=models.CASCADE,null=True)
    date=models.DateField(auto_now_add=True)
