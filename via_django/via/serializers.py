from rest_framework import serializers
from .models import Project, Image


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'filename', 'size', 'file_attributes',
                  'regions',
                  'project', 'edited_by', 'edit_date']
