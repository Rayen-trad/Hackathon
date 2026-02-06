from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_audio, name='upload'),
    path('report/', views.report_view, name='report'),
    path('manager/', views.admin_dashboard, name='manager'),
    path('api/chat/', views.therapy_chat, name='therapy_chat'),
    path('chat/', views.therapy_chat_page, name='therapy_chat_page'),
]
