from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.alignment_home, name='alignment_home'),
    path('best_alignment', views.best_alignment, name='best_alignment'),
]
