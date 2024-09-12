from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)  # Task title
    description = models.TextField(blank=True)  # Optional description
    completed = models.BooleanField(default=False)  # Whether the task is completed or not
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the task was created

    def __str__(self):
        return self.title 
