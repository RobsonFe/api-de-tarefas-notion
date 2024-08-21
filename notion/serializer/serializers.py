from rest_framework import serializers
from notion.models.entity.notion import Notion


class NotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notion
        fields = "__all__"
