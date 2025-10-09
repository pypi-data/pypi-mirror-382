from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('render', views.render_markdown, name='render_markdown'),
    path('health', views.health_check, name='health_check'),
]