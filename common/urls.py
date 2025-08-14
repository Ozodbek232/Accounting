from django.urls import path
from common import views


app_name = "common"


urlpatterns = [
    path('manager/user-list/', views.CustomUserListView.as_view(), name='user-list'),
    path('manager/user-create/', views.CustomUserCreateView.as_view(), name='user-create'),
    path('manager/user/<int:pk>/update', views.CustomUserUpdateView.as_view(), name='user-update'),
    path('manager/user/<int:pk>/delete/', views.CustomUserDeleteView.as_view(), name='user-delete'),
    
    path('user/<int:pk>/info/', views.CustomUserView.as_view(), name='user-info' ),
    path('manager/user/<int:pk>/info/update', views.CustomUserInfoUpdateView.as_view(), name='user-info-update' ),

    path("", views.HomeView.as_view(), name="home"),

    path("manager/seller/", views.SellerListView.as_view(), name="seller-list"),
    path("manager/seller/create/", views.SellerCreateView.as_view(), name="seller-create"),
    path("manager/seller/<int:pk>update/", views.SellerUpdateView.as_view(), name="seller-update"),
    path("manager/seller/<int:pk>delete/", views.SellerDeleteView.as_view(), name="seller-delete"),


    path("manager/product/category/", views.ProductCategoryListView.as_view(), name="category-list"),
    path("manager/product/category/create/", views.ProductCategoryCreateView.as_view(), name="category-create"),
    path("manager/product/category/<int:pk>update/", views.ProductCategoryUpdateView.as_view(), name="category-update"),
    path("manager/product/category/<int:pk>delete/", views.ProductCategoryDeleteView.as_view(), name="category-delete"),


    path("manager/product/", views.ProductListView.as_view(), name="product-list"),
    path("manager/product/create/", views.ProductCreateView.as_view(), name="product-create"),
    path("manager/product/<int:pk>update/", views.ProductUpdateView.as_view(), name="product-update"),
    path("manager/product/<int:pk>delete/", views.ProductDeleteView.as_view(), name="product-delete"),

    
    # Asosiy sahifalar
    path('search-products/', views.search_products, name='search_products'),

    # Sotuvlar
    path('credit/sale/', views.credit_sale, name='sale_credit'),  # Yangi sotuv saqlash
    path('sale/create/', views.sale, name='sale-create'),  # Yangi sotuv saqlash
    path('sale/<int:sale_id>/make-payment/', views.make_payment, name='make_payment'),  # Nasiya to'lovi
    path('add-payment/<int:sale_id>/', views.add_payment, name='add_payment'),  # Yangi to'lov qo'shish
    path('save-sale/', views.save_sale, name='save_sale'),  # Yangi sotuv saqlash
    path('sale/mark-as-paid/', views.mark_sale_as_paid, name='mark_sale_as_paid'),  # To'liq to'lash
    path('sale/detail/<int:sale_id>/', views.sale_details_ajax, name='sale-detail'),
    # Modal va API
    path('create-payment-modal/<int:sale_id>/', views.create_payment_modal, name='payment_modal'),
    path('pending-payments-api/', views.pending_payments_api, name='pending_payments_api'),  # JS bilan moslashtirildi
    path('payment-statistics-api/', views.payment_statistics_api, name='payment_statistics_api'),


    # Sahifalar
    path('pending-payments/', views.pending_payments_view, name='pending_payments'),
    path('sale/', views.SaleListView.as_view(), name='sale-list'),
]


# Qo'shimcha view'lar (ixtiyoriy)
"""
def sales_cart_view(request):
    '''Sotuv korzinasi sahifasi'''
    return render(request, 'manager/sale/cart.html')

def dashboard_view(request):
    '''Asosiy sahifa'''
    return render(request, 'manager/dashboard.html')

@csrf_exempt
def sale_details(request, sale_id):
    '''Sotuv tafsilotlarini ko'rish'''
    if request.method == "GET":
        try:
            sale = get_object_or_404(models.Sale, pk=sale_id)
            
            # Sotuv elementlari
            items = []
            for item in sale.items.all():
                items.append({
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'discount': item.discount,
                    'total': item.total
                })
            
            # To'lovlar tarixi
            payments = []
            for payment in sale.payments.all():
                payments.append({
                    'payment_type': payment.get_payment_type_display(),
                    'amount': payment.amount,
                    'date': payment.date.strftime('%d.%m.%Y %H:%M'),
                    'description': payment.description
                })
            
            return JsonResponse({
                'status': 'success',
                'sale': {
                    'id': sale.id,
                    'client_name': sale.client_full_name,
                    'client_phone': sale.client_phone,
                    'date': sale.date.strftime('%d.%m.%Y %H:%M'),
                    'total_price': sale.total_price,
                    'paid_amount': sale.paid_amount,
                    'remaining_amount': sale.remaining_amount,
                    'status': sale.get_status_display(),
                    'items': items,
                    'payments': payments
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def delete_payment(request, payment_id):
    '''To'lovni o'chirish (faqat admin uchun)'''
    if request.method == "POST":
        try:
            payment = get_object_or_404(models.Payment, pk=payment_id)
            sale = payment.sale
            
            # Faqat admin yoki superuser o'chira oladi
            if not request.user.is_staff:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ruxsat yo\'q'
                }, status=403)
            
            payment.delete()
            
            # Sale'ni yangilash
            sale.update_totals()
            
            return JsonResponse({
                'status': 'success',
                'message': 'To\'lov o\'chirildi',
                'remaining_amount': sale.remaining_amount,
                'paid_amount': sale.paid_amount
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)
"""
