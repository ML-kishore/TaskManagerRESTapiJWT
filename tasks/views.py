from django.shortcuts import render
from django.http import HttpResponse
from tasks.serializers import RegisterSerializer,TaskSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from .models import Tasks

# Create your views here.
def hello(request):
    return HttpResponse("<h1>Testing....</h1>")

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message" : "User has registered Successfully...."},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({"message" : "Task has been created..."},status=status.HTTP_201_CREATED)
    return Response({"errors" : str(serializer.errors)},status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','DELETE','PUT'])
@permission_classes([IsAuthenticated])
def view_task(request, task_id):
    try:
        task = Tasks.objects.get(id=task_id)
    except Tasks.DoesNotExist:
        return Response({"error": "Task not found"}, status=404)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        task.delete()
        return Response({"message": f"Task {task_id} deleted"}, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = TaskSerializer(instance=task,data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message" : f"Task {task_id} updated successfully...."},status=status.HTTP_202_ACCEPTED)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_tasks(request):
    if request.method == 'GET':
        tasks = Tasks.objects.all()
        serializer = TaskSerializer(tasks,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_by_filters(request):
    if request.method == 'GET':
        tasks = Tasks.objects.all()
        print(request.query_params)
        status_param = request.query_params.get('status')
        priority_param = request.query_params.get('priority')

        status_values = [c[0] for c in Tasks.status_choices]
        priority_values = [p[0] for p in Tasks.priority_choices]
        if status_param:
            if status_param not in status_values:
                return Response({"error" : "Status Query Param not exist...."},status=status.HTTP_404_NOT_FOUND)
        
        if priority_param:
            if priority_param not in priority_values:
                return Response({"error" : "Priority Query Param not exist...."},status=status.HTTP_404_NOT_FOUND)

        if status_param:
            print(status_param)
            tasks = tasks.filter(status=status_param)

        if priority_param:
            tasks = tasks.filter(priority=priority_param)

        serializer = TaskSerializer(tasks,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)





