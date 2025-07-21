from django.apps import AppConfig


class AiAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_assistant'
    
    def ready(self):
        from .utils.schema_manager import initialize_schemas
        initialize_schemas()
