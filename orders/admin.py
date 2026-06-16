from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from .services import OrderServiceError, cancel_order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            old_status = Order.objects.values_list('status', flat=True).get(pk=obj.pk)
            if obj.status == Order.Status.CANCELLED:
                if old_status == Order.Status.PENDING:
                    try:
                        cancel_order(obj)
                    except OrderServiceError as exc:
                        raise ValidationError(exc.message) from exc
                    return
                if old_status != Order.Status.CANCELLED:
                    raise ValidationError('Only pending orders can be cancelled.')

        super().save_model(request, obj, form, change)
