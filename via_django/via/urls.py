from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.decorators.csrf import ensure_csrf_cookie

from . import views

app_name = 'via'
urlpatterns = [
    path('', login_required(views.ProjectOverview.as_view()), name='overview'),
    path('<int:pk>/', login_required(ensure_csrf_cookie(views.ProjectView.as_view())), name='project'),
]
