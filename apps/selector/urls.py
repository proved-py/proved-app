"""
dashboard URL Configuration
"""

from django.urls import path

from . import views

urlpatterns = [
    path('selector/', views.selector, name='selector'),
]
