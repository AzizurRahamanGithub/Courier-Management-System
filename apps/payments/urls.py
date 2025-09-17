from django.urls import path
from .views import CreateCheckoutSessionView, ConfirmPaymentView, payment_cancel,payment_success
from . import views

urlpatterns = [
    path('create-checkout-session/<int:order_id>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('confirm-payment/<int:order_id>/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    
     # success & cancel
    path('payment-success/', payment_success, name='payment-success'),
    path('payment-cancel/', payment_cancel, name='payment-cancel'),
]
