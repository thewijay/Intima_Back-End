from django.contrib import admin
from .models import ChatMessage

# Register your models here.

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'conversation_id', 'model_used', 'timestamp')
    list_filter = ('model_used', 'timestamp')
    search_fields = ('question', 'answer', 'user__username', 'conversation_id', 'message_id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)