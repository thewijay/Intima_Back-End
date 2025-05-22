from django.core.management.base import BaseCommand
from ai_assistant.utils.schema_manager import initialize_schemas

class Command(BaseCommand):
    help = 'Initialize Weaviate schemas with proper authentication'
    
    def handle(self, *args, **options):
        self.stdout.write('Initializing Weaviate schemas...')
        initialize_schemas()
        self.stdout.write(self.style.SUCCESS('Successfully initialized Weaviate schemas'))
