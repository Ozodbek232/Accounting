from django.contrib import admin
from common import models

admin.site.register(models.Seller)
admin.site.register(models.ProductCategory)
admin.site.register(models.Product)
admin.site.register(models.CashRegister)
admin.site.register(models.CashFlowCategory)
# admin.py uchun qo'shimcha
from .models import Sale, SaleItem, Payment

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('total',)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_full_name', 'client_phone', 'date', 'total_price', 'paid_amount', 'remaining_amount', 'status']
    list_filter = ['status', 'date', 'client_due_date']
    search_fields = ['client_full_name', 'client_phone']
    readonly_fields = ['total_price', 'paid_amount', 'remaining_amount', 'date']
    inlines = [SaleItemInline, PaymentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items', 'payments')

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'price', 'discount', 'total']
    list_filter = ['sale__date', 'product__category']
    search_fields = ['product__name', 'sale__client_full_name']
    readonly_fields = ['total']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['sale', 'payment_type', 'amount', 'date']
    list_filter = ['payment_type', 'date']
    search_fields = ['sale__client_full_name', 'description']


