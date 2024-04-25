"""
URL configuration for JuniorHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from vacancies.views import page_not_found
from django.conf.urls import handler404


urlpatterns = [
    path('admin/', admin.site.urls),
    path('vacancies/', include('vacancies.urls')),
    path('users/', include('users.urls')),
    path('404/', page_not_found),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

django.conf.urls.handler404 = 'vacancies.views.page_not_found'
