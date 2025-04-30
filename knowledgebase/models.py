from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class AIDocument(models.Model):
    title = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'is_superuser': True},
        related_name='uploaded_ai_documents'
    )
    document = models.FileField(upload_to='ai_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
