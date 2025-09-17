from django.db import models

# Create your models here.
from django.db import models
from apps.accounts.models import User
from apps.orders.models import Order

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    stripe_session_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='usd')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    customer_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} - {self.payment_status} - Order #{self.order.id}"

    class Meta:
        ordering = ['-created_at']