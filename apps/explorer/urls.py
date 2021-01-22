"""
dashboard URL Configuration
"""

from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.explorer, name='dashboard'),
]
