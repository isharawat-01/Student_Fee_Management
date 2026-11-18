
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('student_login')),
    path('', include('students.urls')),
    path('management/', include('fees.urls')),
]
