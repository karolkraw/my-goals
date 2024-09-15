from rest_framework import serializers
from .models import Goal, SubTask

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = '__all__'

class GoalWithSubtasksSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['section_name', 'created_date']

class GoalSerializer(serializers.ModelSerializer):
    # jak bylo odkomentowane to subtasks bylo jednym z pol
    #subtasks = SubTaskSerializer(many=True, write_only=True)  # Use write_only for POST and PUT requests

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['section_name', 'created_date', 'subtasks']


    def create(self, validated_data):
        """ subtasks_data = validated_data.pop('subtasks', []) """
        goal = Goal.objects.create(**validated_data)
        """ for subtask_data in subtasks_data:
            SubTask.objects.create(goal=goal, **subtask_data) """
        return goal

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop('subtasks', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.created_date = validated_data.get('created_date', instance.created_date)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.save()

        # Handle nested subtasks
        existing_subtasks = {subtask.id: subtask for subtask in instance.subtasks.all()}
        for subtask_data in subtasks_data:
            subtask_id = subtask_data.get('id')
            if subtask_id and subtask_id in existing_subtasks:
                subtask = existing_subtasks[subtask_id]
                subtask.title = subtask_data.get('title', subtask.title)
                subtask.completed = subtask_data.get('completed', subtask.completed)
                subtask.deadline = subtask_data.get('deadline', subtask.deadline)
                subtask.save()
            else:
                SubTask.objects.create(goal=instance, **subtask_data)
        
        return instance
