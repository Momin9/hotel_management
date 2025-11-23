from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def housekeeping_dashboard(request):
    return render(request, 'housekeeping/dashboard.html')

@login_required
def task_list(request):
    return render(request, 'housekeeping/task_list.html')