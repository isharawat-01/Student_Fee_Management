
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # AI Assistant
    path('ai/', include('ai_assistant.urls')),
]
