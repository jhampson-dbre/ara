from api import models
from rest_framework import serializers


class PlaybookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Playbook
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Record
        fields = '__all__'
