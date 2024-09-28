from datetime import timezone
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .models import Goal, SubTask
from .serializers import GoalSerializer, SubTaskSerializer, GoalWithSubtasksSerializer
from .my_kafka.KafkaProducer import KafkaProducer
from .my_kafka.KafkaConsumer import KafkaConsumer
from .tasks import retrieve_goal_history
import redis
import os

from confluent_kafka import Consumer



r = redis.StrictRedis(host=os.getenv('REDIS', 'localhost'), port=6379, db=0)


kafka_producer = KafkaProducer()
kafka_consumer = KafkaConsumer()

api_view(['GET'])
def poll_goal_history(request, sectionName):
    # Try fetching the result from Redis
    print("READ FROM REDIS")
    result = r.get(f"goal_history_{sectionName}")

    if result:
        # Decode the byte result to a string and then parse it as JSON
        result_str = result.decode('utf-8')
        result_json = json.loads(result_str)
        print("REturn 200")

        # If result exists in Redis, return it as JSON
        return JsonResponse({"data": result_json}, status=200)
    else:
        # Still processing, no result yet
        return JsonResponse({"status": "processing"}, status=202)


@api_view(['GET'])
def goal_list(request, sectionName):
    if request.method == 'GET':
        goals = Goal.objects.filter(section_name=sectionName).order_by('deadline').reverse()
        serializer = GoalWithSubtasksSerializer(goals, many=True)
        return Response(serializer.data)
    """ producer = KafkaProducer()
    
    producer.send_message('retrieved-goals-topic', 'histdsfory', sectionName)
    
    
    c = Consumer({
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'group.id': 'retrieved-goals-group',
    })
    
    c.subscribe(['retrieved-goals-topic'])
    
    while True:
        msg = c.poll(1.0)

        if msg is None:
            print("NONE")
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        print('Received message: {}'.format(msg.value().decode('utf-8')))

        c.close()
        if request.method == 'GET':
            goals = Goal.objects.filter(section_name=sectionName).order_by('deadline').reverse()
            serializer = GoalWithSubtasksSerializer(goals, many=True)
            return Response(serializer.data) """
    
@api_view(['GET'])
def goal_history_list(request, sectionName):
    if request.method == 'GET':
        #goals = Goal.objects.filter(section_name=sectionName, is_history = True).order_by('completed_date').reverse()
        #serializer = GoalWithSubtasksSerializer(goals, many=True)
        #return Response(serializer.data)


        #kafka_producer.send_message('history-topic', 'history', message=sectionName)
        print("NNNNNNNN: ")
        task = retrieve_goal_history.delay(sectionName)
        #task = retrieve_goal_history(sectionName)
        print("YYYYYYYYYY: ")

        # Return a response with task_id for polling
        return JsonResponse({"task_id": task.id, "status": "processing"}, status=202)
    
        #response_data = kafka_consumer.consume_messages()
        #return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def goal_create(request, sectionName):
    if request.method == 'POST':
        request_data = request.data.copy() 
        request_data['section_name'] = sectionName
        serializer = GoalSerializer(data=request_data)
        if serializer.is_valid():
            # Save the goal instance
            goal = serializer.save()
            
            # Handle nested subtasks if any
            """ subtasks_data = request.data.get('subtasks', [])
            for subtask_data in subtasks_data:
                SubTask.objects.create(goal=goal, **subtask_data) """
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['PUT'])
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['DELETE'])
def goal_delete(request, sectionName, pk):
    try:
        goal = Goal.objects.get(pk=pk)
    except Goal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def complete_goal(request, sectionName, goalTitle):
    try:
        goal = get_object_or_404(Goal, title=goalTitle, sectionName = sectionName)
    except (Goal.DoesNotExist):
        return Response({"error": "Goal or not found."}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PATCH':
        subtasks = goal.subtasks.all()
        serializer = GoalSerializer(goal)

        goal_data = {
            'title': goal.title,
            'description': goal.description,
            'createdDate': goal.created_date,
            'completedDate': timezone.now().date(),
            'section': sectionName,
            'subtasks': subtasks
        }

        kafka_producer.send_message('completed-goals-topic', message=json.dumps(goal_data))
        
        goal.delete()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------- Subtasks Views ----------


    
@api_view(['POST'])
def subtask_create(request, sectionName, goalTitle):
    print("rmkrtmrktm")
    if request.method == 'POST':
        try:
            goal = Goal.objects.get(title=goalTitle, section_name=sectionName)
        except Goal.DoesNotExist:
            return Response({"error": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)

        # Create a copy of the request data and add the goal to it
        data = request.data.copy()
        data['goal'] = goal.id

        # Serialize the data
        serializer = SubTaskSerializer(data=data)
        if serializer.is_valid():
            subtask = serializer.save()  # Save the subtask
            response_data = serializer.data
            """ response_data['goal'] = {
                'id': goal.id,
                'title': goal.title,
                'description': goal.description,
                'created_date': goal.created_date,
                'deadline': goal.deadline
            }  """ # Include information about the goal (task) in the response
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def subtask_detail(request, pk):
    try:
        subtask = SubTask.objects.get(pk=pk)
    except SubTask.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)

@api_view(['PUT'])
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
def subtask_complete(request, goalTitle, subtaskTitle, sectionName):
    try:
        # Retrieve the goal and subtask
        goal = Goal.objects.get(title=goalTitle, section_name=sectionName)
        subtask = SubTask.objects.get(title=subtaskTitle, goal=goal)
    except (Goal.DoesNotExist, SubTask.DoesNotExist):
        return Response({"error": "Goal or Subtask not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        completed_status = request.data.get('completed', None)

        if completed_status is None:
            return Response({"error": "Completed field is required."}, status=status.HTTP_400_BAD_REQUEST)

        subtask.completed = completed_status
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
