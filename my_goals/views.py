from django.utils import timezone
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import Goal, SubTask
from .serializers import GoalSerializer, GoalWithSubtasksKafkaMessageSerializer, SubTaskSerializer, GoalWithSubtasksSerializer
from .my_kafka.KafkaProducer import KafkaProducer
from .my_kafka.KafkaConsumer import KafkaConsumer
from .tasks import retrieve_goal_history
import redis
import os

r = redis.StrictRedis(host=os.getenv('REDIS', 'localhost'), port=6379, db=0)

kafka_producer = KafkaProducer()

api_view(['GET'])
def poll_goal_history(request, sectionName):
    result = r.get(f"goal_history_{sectionName}")

    if result:
        result_str = result.decode('utf-8')
        result_json = json.loads(result_str)
        return JsonResponse({"data": result_json}, status=200)
    else:
        return JsonResponse({"status": "processing"}, status=202)


@api_view(['GET'])
def goal_list(request, sectionName):
    if request.method == 'GET':
        goals = Goal.objects.filter(section_name=sectionName).order_by('deadline').reverse()
        serializer = GoalWithSubtasksSerializer(goals, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
def goal_history_list(request, sectionName):
    if request.method == 'GET':
        task = retrieve_goal_history.delay(sectionName)
        return JsonResponse({"task_id": task.id, "status": "processing"}, status=202)

@api_view(['POST'])
def goal_create(request, sectionName):
    if request.method == 'POST':
        request_data = request.data.copy() 
        request_data['section_name'] = sectionName
        serializer = GoalSerializer(data=request_data)
        if serializer.is_valid():
            goal = serializer.save()
            
            # Handle nested subtasks if any
            """ subtasks_data = request.data.get('subtasks', [])
            for subtask_data in subtasks_data:
                SubTask.objects.create(goal=goal, **subtask_data) """
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def complete_goal(request, sectionName, goalTitle):
    try:
        goal = get_object_or_404(Goal, title=goalTitle, section_name=sectionName)
    except (Goal.DoesNotExist):
        return Response({"error": "Goal or not found."}, status=status.HTTP_404_NOT_FOUND)
    #if request.method == 'PATCH':
    #subtasks = goal.subtasks.all()
    goal.completed_date = timezone.now().date()
    serializer = GoalWithSubtasksKafkaMessageSerializer(goal)
    
    #serializer = GoalSerializer(goal)

    """ goal_data = {
        'title': goal.title,
        'description': goal.description,
        'createdDate': goal.created_date.strftime('%Y-%m-%d'),
        'completedDate': timezone.now().date().strftime('%Y-%m-%d'),
        'section': sectionName,
        'subtasks': list(subtasks.values())
    } """
    
    kafka_producer.send_message(topic='completed-goals-topic', message=json.dumps(serializer.data)) 
    goal.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



# ---------- Subtasks Views ----------


    
@api_view(['POST'])
def subtask_create(request, sectionName, goalTitle):
    print("rmkrtmrktm")
    if request.method == 'POST':
        try:
            goal = Goal.objects.get(title=goalTitle, section_name=sectionName)
        except Goal.DoesNotExist:
            return Response({"error": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['goal'] = goal.id

        serializer = SubTaskSerializer(data=data)
        if serializer.is_valid():
            subtask = serializer.save()
            response_data = serializer.data
            """ response_data['goal'] = {
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'created_date': goal.created_date,
                'deadline': goal.deadline
            }  """
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
def subtask_complete(request, goalTitle, subtaskTitle, sectionName):
    try:
        goal = Goal.objects.get(title=goalTitle, section_name=sectionName)
        subtask = SubTask.objects.get(title=subtaskTitle, goal=goal)
    except (Goal.DoesNotExist, SubTask.DoesNotExist):
        return Response({"error": "Goal or Subtask not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        completed_status = request.data.get('completed', None)

        if completed_status is None:
            return Response({"error": "Completed field is required."}, status=status.HTTP_400_BAD_REQUEST)

        subtask.completed = completed_status
        subtask.completed_date = timezone.now().date()
        subtask.save()

        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def subtask_delete(request, goalTitle, subtaskTitle, sectionName):
    try:
        goal = Goal.objects.get(title=goalTitle, section_name=sectionName)
        subtask = SubTask.objects.get(title=subtaskTitle, goal=goal)
    except SubTask.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
""" @api_view(['PUT'])
def goal_update(request, sectionName, pk):
    try:
        goal = Goal.objects.get(pk=pk)
    except Goal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = GoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            # Save the updated goal instance
            updated_goal = serializer.save()

            # Handle nested subtasks
            SubTask.objects.filter(goal=updated_goal).delete()  # Remove existing subtasks
            subtasks_data = request.data.get('subtasks', [])
            for subtask_data in subtasks_data:
                SubTask.objects.create(goal=updated_goal, **subtask_data)
                
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """

""" @api_view(['DELETE'])
def goal_delete(request, sectionName, pk):
    try:
        goal = Goal.objects.get(pk=pk)
    except Goal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) """
        
""" @api_view(['GET'])
def subtask_detail(request, pk):
    try:
        subtask = SubTask.objects.get(pk=pk)
    except SubTask.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data) """

""" @api_view(['PUT'])
def subtask_update(request, pk):
    try:
        subtask = SubTask.objects.get(pk=pk)
    except SubTask.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = SubTaskSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """
