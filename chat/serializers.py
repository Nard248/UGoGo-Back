from rest_framework import serializers
from .models import DirectThread, DirectMessage

class DirectThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectThread
        fields = ["id", "user1", "user2", "created_at", "last_message_at"]
        read_only_fields = ["id", "created_at", "last_message_at"]

class DirectMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = DirectMessage
        fields = ["id", "thread", "sender", "content", "created_at"]
        read_only_fields = ["id", "created_at", "sender", "thread"]
