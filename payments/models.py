# payments/models.py

from django.db import models

class Payment(models.Model):
    btc_payserver_invoice_id = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True) # auto_now_add=T is not used to allow for manual creation
    paid_at = models.DateTimeField(null=True, blank=True)
