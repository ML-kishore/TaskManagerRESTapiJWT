from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse
from tasks.serializers import RegisterSerializer,TaskSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Tasks
from django.utils import timezone
from datetime import timedelta


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
        task = Tasks.objects.filter(is_deleted=False,user=request.user).get(id=task_id)
    except Tasks.DoesNotExist:
        return Response({"error": "Task not found"}, status=404)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'DELETE':
        task = task.is_deleted = True
        task.save()
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
        tasks = Tasks.objects.filter(is_deleted=False,user=request.user)
        serializer = TaskSerializer(tasks,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_by_filters(request):
    if request.method == 'GET':
        tasks = Tasks.objects.filter(user=request.user,is_deleted=False)

        search = request.query_params.get("search")
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) | Q(desc__icontains=search)
            )
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

        ordering = request.query_params.get("ordering")
        ORDERS = ["created_at","-created_by","status","-status","priority","-priority"]

        if ordering:
            if ordering not in ORDERS:
                return Response({"message":"Invalid Ordering Try Again"},400)
            tasks=tasks.order_by(ordering)

        overdue = request.query_params.get("overdue")
        due = request.query_params.get("due")

        if overdue == "true":
            tasks = tasks.filter(
                due_date__lt = timezone.now()
            ).exclude(status="COMPLETED")

        if due == "today":
            today = timezone.now().date()
            tasks = tasks.filter(
                due_date__date = today                
            ).exclude(status="COMPLETED")

        if due == "thisweek":
            today = timezone.now().date()
            week_end = today + timedelta(days=7)
            tasks = tasks.filter(
                due_date__date__range = [today,week_end]
            )
        #pagination

        paginator = PageNumberPagination()

        paginator.page_size = 5

        result_page = paginator.paginate_queryset(tasks,request)

        serializer = TaskSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def update_status(request,task_id):
    try:
        task = Tasks.objects.get(id=task_id,user=request.user,is_deleted=False)
    except Tasks.DoesNotExist:
        return Response({"message" : "Task Does not Exist"},status=404)
    
    status_choice = request.data.get('status')
    
    if not status_choice:
        return Response({"message": "Status is Required"},status=400)
    
    categories = [c[0] for c in Tasks.status_choices]

    if status_choice not in categories:
        return Response({"message":"Status Is Not Valid Choice"},status=400)
    
    previous_choice = task.status
    task.status = status_choice
    task.save()

    serializer = TaskSerializer(task)
    return Response({"message":f"Status has been changed from {previous_choice} to {status_choice}"},status=200)

@api_view(['PUT','PATCH'])
@permission_classes([IsAuthenticated])
def update_priority(request,task_id):
    try:
        task = Tasks.objects.get(id=task_id,user=request.user)
    except Tasks.DoesNotExist:
        return Response({"message" : "Task Does not Exist"},status=404)
    
    priority = request.data.get('priority')
    
    if not priority:
        return Response({"message": "Priority is Required"},status=400)
    
    categories = [c[0] for c in Tasks.priority_choices]

    if priority not in categories:
        return Response({"message":"Priority Is Not Valid Choice"},status=400)
    
    previous_choice = task.priority
    task.priority = priority
    task.save()

    serializer = TaskSerializer(task)
    return Response({"message":f"Priority has been changed from {previous_choice} to {priority}"},status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stats(request):
    qs = Tasks.objects.filter(is_deleted=False,user=request.user)

    data = {
        "total" : qs.count(),
        "pending" : qs.filter(status='PENDING').count(),
        "completed" : qs.filter(status='COMPLETED').count(),
        "in_progress" : qs.filter(status='IN_PROGRESS').count()

    }
    return Response(data,status=200)
    
    