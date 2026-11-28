from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('ai/', include('ai_assistant.urls')),

    path('library/', include('library.urls')),

    path('dashboard/', include('dashboard.urls')),
    
    path('courses/', include('courses.urls')),

    path('subjects/', include('subjects.urls')),
]