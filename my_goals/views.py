from django.shortcuts import render, redirect, get_object_or_404
from .models import Task

# Display all tasks
def task_list(request):
    tasks = Task.objects.all()  # Get all tasks from the database
    return render(request, 'my_goals/task_list.html', {'tasks': tasks})

# Add a new task
def add_task(request):
    if request.method == 'POST':
        title = request.POST['title']
        Task.objects.create(title=title)
        return redirect('task_list')  # Redirect to the task list after adding the task
    return render(request, 'my_goals/add_task.html')

# Mark task as complete
def complete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    task.completed = True
    task.save()
    return redirect('task_list')

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST.get('description', '')
        task.save()
        return redirect('task_list')
    return render(request, 'todo/edit_task.html', {'task': task})

# Delete an existing task
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('task_list')
