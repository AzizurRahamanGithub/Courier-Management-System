import stripe
from django.conf import settings
from rest_framework import status
from apps.core.base import BaseAPIView
from apps.orders.models import Order

from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    template_name = 'home.html'

class CreatePaymentIntentView(BaseAPIView):
    def post(self, request, order_id):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if order.is_paid:
            return self.error_response(
                message="Payment failed", 
                data={"error": "Order is already paid"}, 
                status_code=status.HTTP_409_CONFLICT
            )
        
        try:
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=int(order.delivery_cost * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id
                }
            )
            
            return self.success_response(
                message="Payment intent created successfully", 
                data={
                    'clientSecret': intent['client_secret'],
                    'amount': order.delivery_cost,
                    'order_id': order.id
                }
            )
        
        except Exception as e:
            return self.error_response(
                message="Payment intent creation failed", 
                data={"error": str(e)}, 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmPaymentView(BaseAPIView):
    def post(self, request, order_id):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return self.error_response(
                message="Payment confirmation failed", 
                data={"error": "Payment intent ID is required"}, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Retrieve the payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Update order payment status
                order.is_paid = True
                order.save()
                
                return self.success_response(
                    message="Payment confirmed successfully", 
                    data={'order_id': order.id, 'paid': True}
                )
            else:
                return self.error_response(
                    message="Payment not completed", 
                    data={"error": "The payment was not successfully processed"}, 
                    status_code=status.HTTP_402_PAYMENT_REQUIRED
                )
        
        except Exception as e:
            return self.error_response(
                message="Payment confirmation failed", 
                data={"error": str(e)}, 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )