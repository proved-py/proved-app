from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.best_alignment, name='best_alignment'),
]
