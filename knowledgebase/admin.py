from django.contrib import admin
from .models import AIDocument

# Register your models here.

@admin.register(AIDocument)
class AIDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')
