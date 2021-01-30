from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.uncertainty_home, name='uncertainty_home'),
    path('variant/<int:variant>', views.uncertainty_variant, name='uncertainty_variant'),
    path('variant/<int:variant>/trace/<int:trace>', views.uncertainty_trace, name='uncertainty_trace')
]
