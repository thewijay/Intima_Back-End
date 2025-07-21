from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AIDocument
from .document_processor import process_text_document

@receiver(post_save, sender=AIDocument)
def process_document(sender, instance, created, **kwargs):
    """Process document after it's saved"""
    if created and instance.document:
        # Get the file path
        file_path = instance.document.path
        
        # Process the document
        process_text_document(file_path)
