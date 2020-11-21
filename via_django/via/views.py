from datetime import datetime

from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .models import Project, Image
from .serializers import ProjectSerializer, ImageSerializer


class ProjectView(generic.DetailView):
    model = Project
    template_name = 'via/via/via.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['project_list'] = Project.objects.all
        return context


class ProjectOverview(generic.ListView):
    model = Project
    template_name = 'via/projects.html'


class ProjectViewSet(viewsets.GenericViewSet,
                     viewsets.generics.RetrieveUpdateAPIView,
                     viewsets.generics.ListCreateAPIView):
    """
    API endpoint that allows projects to be viewed or edited by admins.
    """
    queryset = Project.objects.all().order_by('name')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        try:
            project = self.get_object()
            project.attributes = request.data.get("attributes")
            project.settings = request.data.get("settings")
            print(f"updating project with settings len: {len(project.settings)} attributes: {project.attributes}")
            project.save()

            serializer = self.get_serializer(project, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(e)
            raise
        self.perform_update(serializer)

        return Response(serializer.data)


class ImageViewSet(viewsets.GenericViewSet,
                   viewsets.generics.RetrieveUpdateAPIView,
                   viewsets.generics.ListCreateAPIView):
    """
    API endpoint that allows images to be viewed or edited.
    """
    queryset = Image.objects.all().order_by('id')
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['project', 'edited_by']

    def create(self, request, *args, **kwargs):
        project_id = request.data.get('project')
        project = Project.objects.get(id=project_id)
        result = []
        for f in request.data.getlist('images'):
            i = Image.objects.create(filename=f, project=project)
            result.append(i)
        try:
            serializer = self.get_serializer(result, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(e)

    def update(self, request, *args, **kwargs):
        try:
            image = self.get_object()
            image.regions = request.data.get("regions")
            print(f"updating image with regions {image.regions}")
            image.file_attributes = request.data.get("file_attributes")
            image.edited_by = request.user
            image.edit_date = datetime.now()
            image.save()

            serializer = self.get_serializer(image, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(e)
            raise
        self.perform_update(serializer)

        return Response(serializer.data)

