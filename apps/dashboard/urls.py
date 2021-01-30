from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('variant/<int:variant>', views.dashboard_variant, name='dashboard_variant'),
    path('variant/<int:variant>/trace/<int:trace>', views.dashboard_trace, name='dashboard_trace')
]