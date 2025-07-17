import uuid
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_id = models.CharField(max_length=100, unique=True, null=True, blank=True)  # Frontend conversation ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True)  # Optional: set after first message
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title or f"Conversation {self.id}"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message_id = models.CharField(max_length=100, unique=True)
    question = models.TextField()
    answer = models.TextField()
    model_used = models.CharField(max_length=100)
    sources = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Message {self.message_id} by {self.user.username}"

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

