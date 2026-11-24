
from django.urls import path
from . import views

urlpatterns = [

    path('', views.ai_chat, name='ai_chat'),

    path(
        'upload-timetable/',
        views.upload_timetable,
        name='upload_timetable'
    ),

    path(
        'save-timetable/',
        views.save_timetable,
        name='save_timetable'
    ),

    path(
        'upload-attendance/',
        views.upload_attendance,
        name='upload_attendance'
    ),

    path(
        'save-attendance/',
        views.save_attendance,
        name='save_attendance'
    ),

]
