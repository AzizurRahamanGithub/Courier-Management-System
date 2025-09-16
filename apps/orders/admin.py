from django.contrib import admin
from .models import Order, TrackingHistory

class TrackingHistoryInline(admin.TabularInline):
    model = TrackingHistory
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'delivery_man', 'status', 'delivery_cost', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'created_at', 'user', 'delivery_man')
    search_fields = ('id', 'user__username', 'delivery_man__username', 'recipient_name', 'recipient_phone')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'delivery_man', 'status', 'is_paid')
        }),
        ('Package Details', {
            'fields': ('pickup_address', 'delivery_address', 'recipient_name', 
                      'recipient_phone', 'package_description', 'package_weight')
        }),
        ('Financial Information', {
            'fields': ('delivery_cost',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TrackingHistoryInline]
    
    def get_queryset(self, request):
        # Admin can see all orders
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        # If assigning a delivery man and status is pending, change to assigned
        if obj.delivery_man and obj.status == 'pending':
            obj.status = 'assigned'
        
        super().save_model(request, obj, form, change)
        
        # Create tracking history if status changed
        if change:
            original_obj = self.model.objects.get(pk=obj.pk)
            if original_obj.status != obj.status:
                TrackingHistory.objects.create(
                    order=obj,
                    status=obj.status,
                    notes=f"Status changed from {original_obj.status} to {obj.status} via admin panel"
                )

class TrackingHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'location', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'notes', 'location')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_queryset(self, request):
        # Admin can see all tracking history
        return super().get_queryset(request)

admin.site.register(Order, OrderAdmin)
admin.site.register(TrackingHistory, TrackingHistoryAdmin)