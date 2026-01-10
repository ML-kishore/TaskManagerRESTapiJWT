from django.urls import path
from tasks import views

urlpatterns = [
    path('',views.hello,name='hello'),
    path('register/',views.register,name='register'),
    path('create_task/',views.create_task,name='create_task'),
    path('tasks/',views.view_tasks,name='tasks'),
    path('tasks/<int:task_id>/',views.view_task,name='task_by_id'),
    path('tasks/filter/',views.view_by_filters,name='tasks_with_params')
]
