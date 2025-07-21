from rest_framework import serializers
from django.utils.dateformat import format
from .models import Conversation, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'conversation_id', 'title', 'created_at', 'last_updated', 'last_message']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return {
                'id': last_msg.id,
                'text': last_msg.answer,  # or last_msg.question if you prefer
                'timestamp': format(last_msg.timestamp, 'Y-m-d H:i:s'),
            }
        return None
