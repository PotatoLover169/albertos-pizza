from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='login_dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
