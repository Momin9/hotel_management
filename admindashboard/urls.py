from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='dashboard'),
    path('team/', views.team_list, name='team-list'),
    path('team/<int:pk>/', views.team_profile, name='team-profile'),
    path('team/add/', views.team_add, name='team-add'),
    path('team/update/<int:pk>/', views.team_update, name='team-update'),
]
