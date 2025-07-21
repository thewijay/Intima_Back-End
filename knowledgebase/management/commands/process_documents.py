import os
from django.core.management.base import BaseCommand
from django.conf import settings
from knowledgebase.document_processor import process_all_text_documents

class Command(BaseCommand):
    help = 'Process all documents in the documents directory'
    
    def handle(self, *args, **options):
        self.stdout.write('Processing text documents...')
        count = process_all_text_documents()
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {count} documents'))
