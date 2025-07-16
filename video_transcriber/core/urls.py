from django.urls import path
from .views import upload_view, dashboard_view

urlpatterns = [
    path('upload/', upload_view, name='upload'),
    path('dashboard/', dashboard_view, name='dashboard'),
]