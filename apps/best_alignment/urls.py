from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.alignments_home, name='alignments_home'),
    path('variant/<int:variant>', views.best_alignment, name='best_alignment'),
]
