"""
NAC LMS Backend - Main URL Configuration
Next Art Creations | Intern: Dhruv Sharma
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',       include('apps.authentication.urls')),
    path('api/courses/',    include('apps.courses.urls')),
    path('api/enrollment/', include('apps.enrollment.urls')),
    path('api/dashboard/',  include('apps.dashboard.urls')),
]
