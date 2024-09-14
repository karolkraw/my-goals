from django.db import models
from django.utils import timezone

class Goal(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_date = models.DateField(default=timezone.now)  # Set default to current date
    deadline = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

class SubTask(models.Model):
    goal = models.ForeignKey(Goal, related_name='subtasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_date = models.DateField(default=timezone.now)  # Set default to current date
    deadline = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title

