from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def maintenance_dashboard(request):
    return render(request, 'maintenance/dashboard.html')

@login_required
def issue_list(request):
    return render(request, 'maintenance/issue_list.html')