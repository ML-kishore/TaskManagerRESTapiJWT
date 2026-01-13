from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tasks(models.Model):
    status_choices = (("IN_PROGRESS","In_progress"),("PENDING","Pending"),("COMPLETED","Completed"))
    priority_choices = (("HIGH","High"),("MODERATE","Moderate"),("LOW","Low"))
    title = models.CharField(max_length=100)
    desc = models.TextField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_tasks')
    priority = models.CharField(max_length=10,choices=priority_choices,default='LOW')
    status = models.CharField(max_length=15,choices=status_choices,default="IN_PROGRESS")
    due_date = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.title
    
