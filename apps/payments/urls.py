from django.urls import path
from .views import CreatePaymentIntentView, ConfirmPaymentView, HomePageView

urlpatterns = [
    path('create-payment-intent/<int:order_id>/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('confirm-payment/<int:order_id>/', ConfirmPaymentView.as_view(), name='confirm-payment'),
     path('', HomePageView.as_view(), name='home'),
]