from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Goal, SubTask
from .serializers import GoalSerializer, SubTaskSerializer, GoalWithSubtasksSerializer
from django.views.decorators.csrf import csrf_exempt


# ---------- Goals Views ----------

@api_view(['GET'])
def goal_list(request, sectionName):
    if request.method == 'GET':
        goals = Goal.objects.all()
        #goals = Goal.objects.filter(section_name=sectionName)
        serializer = GoalWithSubtasksSerializer(goals, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def goal_create(request, sectionName):
    if request.method == 'POST':
        data = request.data.copy() 
        data['section_name'] = sectionName
        serializer = GoalSerializer(data=request.data)
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
@api_view(['GET'])
def goal_detail(request, sectionName, pk):
    try:
        goal = Goal.objects.get(pk=pk)
    except Goal.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GoalSerializer(goal)
        return Response(serializer.data)

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

@csrf_exempt
def complete_goal(request, sectionName, goal_id):
    goal = get_object_or_404(Goal, pk=goal_id)
    print("Sdfikdfm")
    goal.mark_as_completed()
    return JsonResponse({'message': 'Goal marked as completed and Kafka message sent!'})


# ---------- Subtasks Views ----------

@api_view(['GET'])
def subtask_list(request):
    if request.method == 'GET':
        subtasks = SubTask.objects.all()
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data)

@api_view(['POST'])
def subtask_create(request):
    if request.method == 'POST':
        serializer = SubTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

@api_view(['DELETE'])
def subtask_delete(request, pk):
    try:
        subtask = SubTask.objects.get(pk=pk)
    except SubTask.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
