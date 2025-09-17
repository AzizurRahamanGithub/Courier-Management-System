from django.urls import path
from .views import (
    OrderListCreateView, OrderDetailView, OrderStatusUpdateView,
    AssignDeliveryManView, OrderTrackingView
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('<int:pk>/assign/', AssignDeliveryManView.as_view(), name='assign-delivery-man'),
    path('<int:pk>/tracking/', OrderTrackingView.as_view(), name='order-tracking'),
    
]