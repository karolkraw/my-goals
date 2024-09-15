from django.urls import path
from . import views

urlpatterns = [
    # ---------- Goals URLs ----------
    path('goals/<str:sectionName>/', views.goal_list, name='goal-list'),
    path('goals/create/<str:sectionName>/', views.goal_create, name='goal-create'),
    path('goals/<str:sectionName><int:pk>/', views.goal_detail, name='goal-detail'),
    path('goals/update/<str:sectionName>/<int:pk>/', views.goal_update, name='goal-update'),
    path('goals/delete/<str:sectionName>/<int:pk>/', views.goal_delete, name='goal-delete'),
    path('goals/complete/<str:sectionName>/<int:goal_id>/', views.complete_goal, name='complete-goal'),


    # ---------- SubTasks URLs ----------
    path('goals/subtasks/', views.subtask_list, name='subtask-list'),
    path('goals/subtasks/create/<str:sectionName>/<str:goalTitle>/', views.subtask_create, name='subtask-create'),
    path('goals/subtasks/<int:pk>/', views.subtask_detail, name='subtask-detail'),
    path('goals/subtasks/<int:pk>/update/', views.subtask_update, name='subtask-update'),
    path('goals/subtasks/delete/<str:sectionName>/<str:taskTitle>/<str:subtaskTitle>/', views.subtask_delete, name='subtask-delete'),
]
