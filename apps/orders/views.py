from rest_framework import status
from apps.core.base import BaseAPIView
from .models import Order, TrackingHistory
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    AssignDeliveryManSerializer, TrackingHistorySerializer
)
import stripe
from django.contrib.sites.shortcuts import get_current_site


class OrderListCreateView(BaseAPIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        user = request.user
        
        if user.role == 'admin':
            orders = Order.objects.all()
        elif user.role == 'delivery_man':
            orders = Order.objects.filter(delivery_man=user)
        else:  # user
            orders = Order.objects.filter(user=user)
        
        serializer = OrderSerializer(orders, many=True)
        return self.success_response(
            message="Orders retrieved successfully", 
            data=serializer.data
        )
    
    def post(self, request):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        if request.user.role == 'delivery_man':
            return self.error_response(
                message="Order creation failed", 
                data={"error": "Only regular users can create orders."},
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            response_serializer = OrderSerializer(order)

            customer_email = (
                request.data.get("email")
                or getattr(request.user, "email", None)
                or "test@example.com"
            )
            try:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
            
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
                    success_url = f"{protocol}://{current_site.domain}/api/v1/payments/payment-success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}",
                    cancel_url = f"{protocol}://{current_site.domain}/api/v1/payments/payment-cancel?order_id={order.id}",
                    customer_email=customer_email,
                    metadata={
                        'order_id': order.id,
                        'user_id': request.user.id
                    }
                )
                checkout_url = checkout_session.url
            except Exception as e:
                checkout_url = None  

            return self.success_response(
                message="Order created successfully",
                data={
                    "order": response_serializer.data,
                     "checkout_url": checkout_session.url,
                    "session_id": checkout_session.id,
                    "email": customer_email
                },
                status_code=status.HTTP_201_CREATED
            )

        return self.error_response(
            message="Order creation failed", 
            data=serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OrderDetailView(BaseAPIView):
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None
    
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        order = self.get_object(pk)
        if not order:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not (request.user.role == 'admin' or 
                (request.user.role == 'delivery_man' and order.delivery_man == request.user) or
                (request.user.role == 'user' and order.user == request.user)):
            return self.error_response(
                message="Permission denied", 
                data={"error": "You don't have permission to view this order"}, 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderSerializer(order)
        return self.success_response(
            message="Order retrieved successfully", 
            data=serializer.data
        )
    
    def put(self, request, pk):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        order = self.get_object(pk)
        if not order:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Only admin or order owner can update order details
        if not (request.user.role == 'admin' or order.user == request.user):
            return self.error_response(
                message="Permission denied", 
                data={"error": "You don't have permission to update this order"}, 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderCreateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message="Order updated successfully", 
                data=serializer.data
            )
        
        return self.error_response(
            message="Order update failed", 
            data=serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        order = self.get_object(pk)
        if not order:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Only admin or order owner can delete order
        if not (request.user.role == 'admin' or order.user == request.user):
            return self.error_response(
                message="Permission denied", 
                data={"error": "You don't have permission to delete this order"}, 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        order.delete()
        return self.success_response(
            message="Order deleted successfully"
        )


class OrderStatusUpdateView(BaseAPIView):
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None
    
    def put(self, request, pk):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        order = self.get_object(pk)
        if not order:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Only delivery man assigned to order or admin can update status
        if not (request.user.role == 'admin' or 
                (request.user.role == 'delivery_man' and order.delivery_man == request.user)):
            return self.error_response(
                message="Permission denied", 
                data={"error": "You don't have permission to update the status of this order"}, 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderStatusUpdateSerializer(order, data=request.data)
        if serializer.is_valid():
            old_status = order.status
            order = serializer.save()
            
            # Create tracking history
            TrackingHistory.objects.create(
                order=order,
                status=order.status,
                notes=f"Status changed from {old_status} to {order.status}"
            )
            
            return self.success_response(
                message="Order status updated successfully", 
                data=serializer.data
            )
        
        return self.error_response(
            message="Status update failed", 
            data=serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )


class AssignDeliveryManView(BaseAPIView):
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None
    
    def put(self, request, pk):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        order = self.get_object(pk)
        if not order:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Only admin can assign delivery men
        if not request.user.role == 'admin':
            return self.error_response(
                message="Permission denied", 
                data={"error": "Only administrators can assign delivery personnel"}, 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = AssignDeliveryManSerializer(order, data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            
            # Update status if it was pending
            if order.status == 'pending':
                order.status = 'assigned'
                order.save()
            
            # Create tracking history
            TrackingHistory.objects.create(
                order=order,
                status='assigned',
                notes=f"Order assigned to delivery man: {order.delivery_man.username}"
            )
            
            return self.success_response(
                message="Delivery man assigned successfully", 
                data=OrderSerializer(order).data
            )
        
        return self.error_response(
            message="Assignment failed", 
            data=serializer.errors, 
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OrderTrackingView(BaseAPIView):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return self.error_response(
                message="Authentication required", 
                status_code=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return self.error_response(
                message="Order not found", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not (request.user.role == 'admin' or 
                (request.user.role == 'delivery_man' and order.delivery_man == request.user) or
                (request.user.role == 'user' and order.user == request.user)):
            return self.error_response(
                message="Permission denied", 
                data={"error": "You don't have permission to view tracking information for this order"}, 
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        tracking_history = order.tracking_history.all()
        serializer = TrackingHistorySerializer(tracking_history, many=True)
        return self.success_response(
            message="Tracking history retrieved successfully", 
            data=serializer.data
        )