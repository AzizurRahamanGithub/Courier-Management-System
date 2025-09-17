import stripe
from django.conf import settings
from rest_framework import status
from apps.core.base import BaseAPIView
from apps.orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def payment_success(request):
    order_id = request.GET.get("order_id")
    session_id = request.GET.get("session_id")

    return render(request, "payment_success.html", {
        "order_id": order_id,
        "session_id": session_id
    })


@csrf_exempt
def payment_cancel(request):
    order_id = request.GET.get("order_id")
    return render(request, "payment_cancel.html", {
        "order_id": order_id
    })

class CreateCheckoutSessionView(BaseAPIView):
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
                message="Order already paid",
                status_code=status.HTTP_409_CONFLICT
            )

        customer_email = (
            request.data.get("email")
            or getattr(request.user, "email", None)
            or "test@example.com"
        )

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Order #{order.id}",
                        },
                        'unit_amount': int(order.delivery_cost * 100),  # cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url = f"http://127.0.0.1:8000/api/v1/payments/payment-success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
                cancel_url = f"http://127.0.0.1:8000/api/v1/payments/payment-cancel?order_id={order.id}",

                customer_email=customer_email,  
                metadata={
                    'order_id': order.id,
                    'user_id': request.user.id
                }
            )

            return self.success_response(
                message="Checkout session created",
                data={
                    "checkout_url": checkout_session.url,
                    "session_id": checkout_session.id,
                    "email": customer_email
                }
            )

        except Exception as e:
            return self.error_response(
                message="Failed to create checkout session",
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

        session_id = request.data.get("session_id")
        if not session_id:
            return self.error_response(
                message="Session ID required",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == "paid":
                order.is_paid = True
                order.save()
                return self.success_response(
                    message="Payment confirmed successfully",
                    data={"order_id": order.id, "paid": True}
                )
            else:
                return self.error_response(
                    message="Payment not completed",
                    data={"error": "Stripe session not paid"},
                    status_code=status.HTTP_402_PAYMENT_REQUIRED
                )

        except Exception as e:
            return self.error_response(
                message="Payment confirmation failed",
                data={"error": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
