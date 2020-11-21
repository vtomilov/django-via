"""via_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from rest_framework import routers

from via.views import ProjectViewSet, ImageViewSet

router = routers.DefaultRouter()
router.register(r'project', ProjectViewSet)
router.register(r'image', ImageViewSet)

urlpatterns = [
    path('', RedirectView.as_view(url='via/')),
    path('api/', include(router.urls)),
    path('via/', include('via.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
] + static('images/', document_root='images/')

