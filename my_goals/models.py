from django.db import models
from django.utils import timezone

from my_goals.my_kafka import KafkaProducer

def get_current_date():
    return timezone.now().date()

class Goal(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_date = models.DateField(default=get_current_date)
    completed_date = models.DateField(null=True)
    deadline = models.DateField(default=get_current_date)
    section_name = models.CharField(max_length=255)

    """  def __str__(self):
        return self.title """

class SubTask(models.Model):
    goal = models.ForeignKey(Goal, related_name='subtasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(default='')
    completed = models.BooleanField(default=False)
    created_date = models.DateField(default=get_current_date)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True)
    deadline = models.DateField(default=get_current_date) 

    def __str__(self):
        return self.title


""" def serialize_goal(self):
        subtasks = self.subtasks.all()
        subtask_list = [
            {
                "id": subtask.id,
                "title": subtask.title,
                "completed": subtask.completed,
                "createdDate": str(subtask.created_date),
                "deadline": str(subtask.deadline)
            }
            for subtask in subtasks
        ]
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "createdDate": str(self.created_date),
            "deadline": str(self.deadline),
            "subtasks": subtask_list
        }

def mark_as_completed(self):
    producer = KafkaProducer()
    goal_data = self.serialize_goal()
    producer.send_message("goal_completed_topic", goal_data) """
