from django.db import models


class PaymentRequest(models.Model):
    payment_id = models.TextField(unique=True)
    success = models.BooleanField()
