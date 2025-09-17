from rest_framework import serializers
from .models import Order, TrackingHistory
from apps.accounts.models import User

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    delivery_man = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'is_paid')


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('delivery_man', 'status', 'is_paid', 'user')


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)


class AssignDeliveryManSerializer(serializers.ModelSerializer):
    delivery_man_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='delivery_man'),
        source='delivery_man',
        write_only=True
    )
    
    class Meta:
        model = Order
        fields = ('delivery_man_id',)


class TrackingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingHistory
        fields = '__all__'
        read_only_fields = ('created_at',)