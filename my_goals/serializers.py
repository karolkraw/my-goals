from rest_framework import serializers
from .models import Goal, SubTask

class SubTaskSerializer(serializers.ModelSerializer):
    #createdDate = serializers.DateField(source='created_date')
    createdDate = serializers.SerializerMethodField()
    completedDate = serializers.SerializerMethodField()
    #deadline = serializers.SerializerMethodField() # used only for serialization
    deadline = serializers.DateField(format='%d-%m-%Y', input_formats=['%d-%m-%Y', '%Y-%m-%d']) # input_formats -> accepted format during deserializing # format - serializing


    class Meta:
        model = SubTask
        fields = ['title', 'description', 'createdDate', 'deadline', 'completedDate', 'completed', 'goal']

    def create(self, validated_data):
        print("lllllllllllllllllllgflllll")
        print(validated_data)
        subtask = SubTask.objects.create(**validated_data)
        print("gfmdkgmdfkgmdkfg")
        print(subtask.deadline)
        return subtask 
    
    def get_createdDate(self, obj):
        return obj.created_date.strftime('%d-%m-%Y')

    def get_completedDate(self, obj):
        return obj.completed_date.strftime('%d-%m-%Y') if obj.completed_date else None

class GoalWithSubtasksSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    #dateCreated = serializers.DateField(source='created_date')
    createdDate = serializers.SerializerMethodField()
    completedDate = serializers.SerializerMethodField()
    deadline = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ['title', 'description', 'createdDate', 'deadline', 'completedDate', 'subtasks']
        #read_only_fields = ['section_name']

    def get_createdDate(self, obj):
        return obj.created_date.strftime('%d-%m-%Y')

    def get_deadline(self, obj):
        return obj.deadline.strftime('%d-%m-%Y')
    
    def get_completedDate(self, obj):
        return obj.completed_date.strftime('%d-%m-%Y') if obj.completed_date else None
    
class GoalWithSubtasksKafkaMessageSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)
    createdDate = serializers.SerializerMethodField()
    completedDate = serializers.SerializerMethodField()
    sectionName = serializers.CharField(source='section_name')

    class Meta:
        model = Goal
        fields = ['title', 'description', 'createdDate', 'completedDate', 'sectionName', 'subtasks']

    def get_createdDate(self, obj):
        return obj.created_date.strftime('%d-%m-%Y')
    
    def get_completedDate(self, obj):
        return obj.completed_date.strftime('%d-%m-%Y') if obj.completed_date else None

class GoalSerializer(serializers.ModelSerializer):
    #subtasks = SubTaskSerializer(many=True, write_only=True)  # Use write_only for POST and PUT requests

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['created_date', 'subtasks']


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
