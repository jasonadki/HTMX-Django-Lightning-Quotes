from django.db import models
from django.conf import settings
import uuid

from payments.models import Payment

class Quote(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=10, default='pending', choices=STATUS_CHOICES)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    session_token = models.CharField(max_length=255, null=True, blank=True) # This is needed for anonymous quotes

    def __str__(self):
        # Provides a more descriptive name for the object
        return f"Quote {self.id} by {self.user}"

    class Meta:
        # Orders quotes by creation date by default
        ordering = ['-id']
