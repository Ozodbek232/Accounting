from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils import timezone
from common import models, forms
from helpers.views import CreateView, UpdateView, DeleteView
from datetime import date
import json



class HomeView(View):
    def get(self, request):
       return render(request, "index.html")

class SellerListView(ListView):
    model = models.Seller
    template_name = "manager/seller/list.html"
    context_object_name = "objects"
    queryset = model.objects.all().order_by("-id")
    paginate_by = 5
    def get_queryset(self):
        object_list = self.queryset
        search = self.request.GET.get("search", None)
        if search:
            object_list = object_list.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))
        return object_list


class SellerCreateView(CreateView):
    model = models.Seller
    form_class = forms.SellerForm
    template_name = "manager/seller/create.html"
    context_object_name = "object"
    success_url = "common:seller-list"
    success_create_url = "common:seller-create"

class SellerUpdateView(UpdateView):
    model = models.Seller
    form_class = forms.SellerForm
    template_name = "manager/seller/update.html"
    context_object_name = "object"
    success_url = "common:seller-list"
    success_update_url = "common:seller-update"


class SellerDeleteView(DeleteView):
    model = models.Seller
    success_url = "common:seller-list"


class ProductCategoryListView(ListView):
    model = models.ProductCategory
    template_name = "manager/product-category/list.html"

    context_object_name = "objects"
    queryset = model.objects.all().order_by("-id")
    paginate_by = 10

    def get_queryset(self):
        object_list = self.queryset
        search = self.request.GET.get("search", None)
        if search:
            object_list = object_list.filter(Q(title__icontains=search))

        return object_list


class ProductCategoryCreateView(CreateView):
    model = models.ProductCategory
    form_class = forms.ProductCategoryForm
    template_name = "manager/product-category/create.html"
    context_object_name = "object"
    success_url = "common:category-list"
    success_create_url = "common:category-create"


class ProductCategoryUpdateView(UpdateView):
    model = models.ProductCategory
    form_class = forms.ProductCategoryForm
    template_name = "manager/product-category/update.html"
    context_object_name = "object"
    success_url = "common:category-list"
    success_update_url = "common:category-update"


class ProductCategoryDeleteView(DeleteView):
    model = models.ProductCategory
    success_url = "common:category-list"



class ProductListView(ListView):
    model = models.Product
    template_name = "manager/product/list.html"

    context_object_name = "objects"
    queryset = model.objects.all().order_by("-id")
    paginate_by = 10

    def get_queryset(self):
        object_list = self.queryset
        search = self.request.GET.get("search", None)
        if search:
            object_list = object_list.filter(Q(name__icontains=search) | Q(category__icontains=search))
        return object_list


class ProductCreateView(CreateView):
    model = models.Product
    form_class = forms.ProductForm
    template_name = "manager/product/create.html"
    context_object_name = "object"
    success_url = "common:product-list"
    success_create_url = "common:product-create"


class ProductUpdateView(UpdateView):
    model = models.Product
    form_class = forms.ProductForm
    template_name = "manager/product/update.html"
    context_object_name = "object"
    success_url = "common:product-list"
    success_update_url = "common:product-update"


class ProductDeleteView(DeleteView):
    model = models.Product
    success_url = "common:product-list"


def sale(request):
    return render(request, "manager/sale/create.html")

def search_products(request):
    term = request.GET.get("term", "")
    products = models.Product.objects.filter(Q(name__icontains=term))[:10]
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),  
            'amount': product.amount,
            'image': product.image.url if product.image else '',
            'category': product.category.title if product.category else '',
            'max_discount': product.max_discount,  
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def save_sale(request):
    """Sotuvni saqlash - to'lov turini tanlash bilan"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cart_items = data.get('cart_items', {})
            payment_data = data.get('payment', {})
            
            if not cart_items:
                return JsonResponse({'status': 'error', 'message': 'Korzina bo\'sh'}, status=400)
            
            # Yangi sotuv yaratish
            sale = models.Sale.objects.create(
                status='pending',
                paid_amount=0,
                pending_amount=0,
                remaining_amount=0
            )
            
            total_amount = 0
            
            # Har bir mahsulot uchun SaleItem yaratish
            for product_id, item_data in cart_items.items():
                try:
                    product = models.Product.objects.get(id=product_id)
                    quantity = int(item_data['quantity'])
                    discount_per_item = float(item_data['discount'])
                    
                    if product.amount < quantity:
                        return JsonResponse({
                            'status': 'error', 
                            'message': f'{product.name} - mavjud miqdor: {product.amount}, so\'ralgan: {quantity}'
                        }, status=400)
                    
                    sale_item = models.SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        discount=discount_per_item,
                        total=(product.price - discount_per_item) * quantity
                    )
                    
                    total_amount += sale_item.total
                    
                    # Mahsulot miqdorini kamaytirish
                    product.amount -= quantity
                    product.save()
                    
                except models.Product.DoesNotExist:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Mahsulot topilmadi: ID {product_id}'
                    }, status=404)
            
            # Sotuv umumiy narxini yangilash
            sale.total_price = total_amount
            sale.pending_amount = total_amount  # Kutilayotgan to'lov
            sale.remaining_amount = total_amount  # Qarz
            
            # Agar to'lov ma'lumotlari berilgan bo'lsa
            if payment_data and payment_data.get('payment_type'):
                payment_type = payment_data.get('payment_type')
                payment_amount = float(payment_data.get('amount', 0))
                client_name = payment_data.get('client_name', '')
                client_phone = payment_data.get('client_phone', '')
                client_due_date = payment_data.get('client_due_date', None)
                description = payment_data.get('description', '')
                
                if payment_amount > 0 and payment_amount <= total_amount:
                    # To'lov yaratish
                    payment = models.Payment.objects.create(
                        sale=sale,
                        payment_type=payment_type,
                        amount=payment_amount,
                        description=description
                    )
                    
                    # Sale'ni yangilash
                    sale.paid_amount = payment_amount
                    sale.pending_amount = max(total_amount - payment_amount, 0)
                    sale.remaining_amount = sale.pending_amount
                    
                    # Mijoz ma'lumotlarini saqlash (agar nasiya bo'lsa)
                    if payment_type == 'credit':
                        sale.client_full_name = client_name
                        sale.client_phone = client_phone
                        if client_due_date:
                            sale.client_due_date = client_due_date
                    
                    # Status'ni o'zgartirish
                    if sale.pending_amount == 0:
                        sale.status = 'paid'
                    else:
                        sale.status = 'partial'
            
            sale.save()
            
            # Javob qaytarish
            if sale.status == 'paid':
                return JsonResponse({
                    'status': 'completed',
                    'sale_id': sale.id,
                    'total_amount': total_amount,
                    'message': 'Sotuv muvaffaqiyatli yakunlandi'
                })
            else:
                return JsonResponse({
                    'status': 'pending',
                    'sale_id': sale.id,
                    'total_amount': total_amount,
                    'pending_amount': sale.pending_amount,  # Kutilayotgan to'lov
                    'remaining_amount': sale.remaining_amount,  # Qarz
                    'redirect_url': '/pending-payments/',
                    'message': 'Sotuv kutilayotgan to\'lovlar ro\'yxatiga qo\'shildi'
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Xatolik yuz berdi: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def add_payment(request, sale_id):
    """To'lov qo'shish"""
    if request.method == "POST":
        try:
            sale = get_object_or_404(models.Sale, pk=sale_id)
            data = json.loads(request.body)
            
            payment_type = data.get('payment_type')
            amount = float(data.get('amount', 0))
            description = data.get('description', '')
            
            client_name = data.get('client_name', '')
            client_phone = data.get('client_phone', '')
            client_due_date = data.get('client_due_date', None)
            
            if amount <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'To\'lov summası 0 dan katta bo\'lishi kerak'
                }, status=400)
            
            if amount > sale.pending_amount:  # pending_amount bilan solishtiramiz
                return JsonResponse({
                    'status': 'error',
                    'message': f'To\'lov summası kutilayotgan to\'lovdan ({sale.pending_amount} UZS) katta bo\'lmasligi kerak'
                }, status=400)
            
            # Nasiya uchun mijoz ma'lumotlarini tekshirish
            if payment_type == 'credit' and (not client_name or not client_phone):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Nasiya uchun mijoz ma\'lumotlari kiritilishi kerak'
                }, status=400)
            
            # To'lov yaratish
            payment = models.Payment.objects.create(
                sale=sale,
                payment_type=payment_type,
                amount=amount,
                description=description
            )
            
            # Sale'ni yangilash
            sale.paid_amount += amount
            sale.pending_amount = max(sale.total_price - sale.paid_amount, 0)
            sale.remaining_amount = sale.pending_amount
            
            # Mijoz ma'lumotlarini saqlash (agar nasiya bo'lsa)
            if payment_type == 'credit':
                sale.client_full_name = client_name
                sale.client_phone = client_phone
                if client_due_date:
                    sale.client_due_date = client_due_date
            
            # Status'ni o'zgartirish
            if sale.pending_amount == 0:
                sale.status = 'paid'
            else:
                sale.status = 'partial'
            
            sale.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'To\'lov muvaffaqiyatli qo\'shildi',
                'pending_amount': sale.pending_amount,
                'remaining_amount': sale.remaining_amount,
                'paid_amount': sale.paid_amount,
                'sale_status': sale.status
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Xatolik yuz berdi: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)


# views.py - pending_payments_api funksiyasini yangilash
def pending_payments_api(request):
    """Kutilayotgan to'lovlar API - faqat kutilayotgan to'lovlari bo'lgan sotuvlar"""
    status_filter = request.GET.get('status', '')
    client_filter = request.GET.get('client', '')
    date_filter = request.GET.get('date', '')
    due_status_filter = request.GET.get('due_status', '')
    
    # Faqat kutilayotgan to'lovi bo'lgan sotuvlarni olish
    sales = models.Sale.objects.filter( pending_amount__gt=0).order_by('-date')
    
    # Har bir sale uchun summalarni qayta hisoblash
    for sale in sales:
        sale.update_totals()
    
    # Filtrlar
    if status_filter:
        sales = sales.filter(status=status_filter)
    
    if client_filter:
        sales = sales.filter(client_full_name__icontains=client_filter)
    
    if date_filter:
        sales = sales.filter(date__date=date_filter)
    
    # Muddat bo'yicha filtr
    if due_status_filter:
        today = timezone.now().date()
        if due_status_filter == 'overdue':
            sales = sales.filter(client_due_date__lt=today, status__in=['pending', 'partial'])
        elif due_status_filter == 'due_soon':
            three_days_later = today + timedelta(days=3)
            sales = sales.filter(client_due_date__lte=three_days_later, client_due_date__gte=today, status__in=['pending', 'partial'])
        elif due_status_filter == 'normal':
            three_days_later = today + timedelta(days=3)
            sales = sales.filter(Q(client_due_date__gt=three_days_later) | Q(client_due_date__isnull=True))
    
    data = []
    for sale in sales:
        payments = []
        for payment in sale.payments.all()[:5]:
            payments.append({
                'payment_type_display': payment.get_payment_type_display(),
                'amount': payment.amount,
                'date': payment.date.strftime('%d.%m.%Y %H:%M')
            })
        
        data.append({
            'id': sale.id,
            'client_name': sale.client_full_name or 'Noma\'lum',
            'client_phone': sale.client_phone or '',
            'client_due_date': sale.client_due_date.isoformat() if sale.client_due_date else None,
            'date': sale.date.strftime('%d.%m.%Y %H:%M'),
            'total_price': sale.total_price,
            'paid_amount': sale.paid_amount,
            'pending_amount': sale.pending_amount,  # Kutilayotgan to'lov
            'remaining_amount': sale.remaining_amount,  # Qarz
            'status': sale.status,
            'payments': payments
        })
    
    return JsonResponse({'sales': data})


# views.py - payment_statistics_api funksiyasini yangilash
def payment_statistics_api(request):
    """To'lov statistikasi API"""
    today = timezone.now().date()
    
    """Nasiyali sotuvni to'landi deb belgilash"""
    # Jami kutilayotgan to'lovlar
    total_pending = models.Sale.objects.filter(pending_amount__gt=0).aggregate(
        total=Sum('pending_amount')
    )['total'] or 0
    # Jami qarzlar
# payment_type = 'credit' bo'lgan jami to'lovlar
    total_credit = models.Payment.objects.filter(
        payment_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Bugun to'langan summalar
    today_payments = models.Payment.objects.filter(
        date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Statuslar bo'yicha sanash
    pending_count = models.Sale.objects.filter(status='pending').count()
    partial_count = models.Sale.objects.filter(status='partial').count()
    paid_count = models.Sale.objects.filter(status='paid').count()
    
    # Muddati o'tgan to'lovlar soni
    overdue_count = models.Sale.objects.filter(
        client_due_date__lt=today,
        status__in=['pending', 'partial']
    ).count()
    
    return JsonResponse({
        'total_pending': total_pending,  
        'total_credit': total_credit,      # Jami qarzlar
        'today_payments': today_payments,
        'pending_count': pending_count,
        'partial_count': partial_count,
        'paid_count': paid_count,
        'overdue_count': overdue_count
    })


@csrf_exempt  
def create_payment_modal(request, sale_id):
    """To'lov modal oynasi uchun ma'lumotlarni qaytarish"""
    if request.method == "GET":
        try:
            sale = get_object_or_404(models.Sale, pk=sale_id)
            
            return JsonResponse({
                'status': 'success',
                'sale': {
                    'id': sale.id,
                    'date': sale.date.strftime('%d.%m.%Y %H:%M'),
                    'total_price': sale.total_price,
                    'paid_amount': sale.paid_amount,
                    'pending_amount': sale.pending_amount,    # Kutilayotgan to'lov
                    'remaining_amount': sale.remaining_amount, # Qarz
                    'client_name': sale.client_full_name or '',
                    'client_phone': sale.client_phone or '',
                    'client_due_date': sale.client_due_date.isoformat() if sale.client_due_date else '',
                    'status': sale.status
                },
                'payment_types': [
                    {'value': 'cash', 'label': 'Naqd'},
                    {'value': 'card', 'label': 'Karta'},
                    {'value': 'credit', 'label': 'Nasiya'},
                    {'value': 'bank_transfer', 'label': 'Bank o\'tkazmasi'},
                ]
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Xatolik yuz berdi: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)
def pending_payments_view(request):
    """Kutilayotgan to'lovlar sahifasi"""
    return render(request, 'manager/sale/pending-payment.html')

class SaleListView(ListView):
    model = models.Payment
    template_name = 'manager/sale/list.html'
    context_object_name = 'objects'
    queryset = models.Payment.objects.filter(payment_type='cash')
    def get_queryset(self):
        object_list = self.queryset
        return object_list
# YANGILANGAN SALE_DETAIL - KLIENT MA'LUMOTLARI BILAN
"""
def sale_detail(request, pk):
    try:
        sale = models.Sale.objects.prefetch_related('items__product').select_related('seller').get(id=pk)
        data = {
            'id': sale.id,
            'date': sale.date.strftime('%Y-%m-%d %H:%M'),
            'seller': sale.seller.name if sale.seller else None,
            'total_price': sale.total_price,
            'cash_amount': sale.cash_amount,
            'credit_amount': sale.credit_amount,
            'client_full_name': sale.client_full_name,
            'client_phone': sale.client_phone,
            'client_due_date': sale.client_due_date.strftime('%Y-%m-%d') if sale.client_due_date else None,
            'items': [
                {
                    'product': item.product.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'discount': item.discount,
                    'total': item.total
                }
                for item in sale.items.all()
            ]
        }
        return JsonResponse({'status': 'ok', 'data': data})
    except models.Sale.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sotuv topilmadi'})

# YANGI FUNKSIYA: Nasiyali sotuvlarni ko'rish
def credit_sales_list(request):
    credit_sales = models.Payment.objects.filter(
        credit_amount__gt=0
    ).prefetch_related('items__product').select_related('seller').order_by('-date')
    
    return render(request, 'sale/credit_list.html', {'credit_sales': credit_sales})

# YANGI FUNKSIYA: Klient bo'yicha qidirish
def search_client(request):
    search_term = request.GET.get('term', '').strip()
    
    if len(search_term) < 2:
        return JsonResponse({'results': []})
    
    # Klient ismi yoki telefon raqam bo'yicha qidirish
    clients = models.Sale.objects.filter(
        Q(client_full_name__icontains=search_term) |
        Q(client_phone__icontains=search_term),
        credit_amount__gt=0
    ).values('client_full_name', 'client_phone').distinct()[:10]
    
    results = [
        {
            'name': client['client_full_name'],
            'phone': client['client_phone']
        }
        for client in clients if client['client_full_name']
    ]
    
    return JsonResponse({'results': results})
# views.py faylingizga qo'shing

@csrf_exempt
@require_POST
def mark_sale_as_paid(request):
    try:
        # POST ma'lumotlarini olish
        sale_id = request.POST.get('sale_id')
        
        # Sale ID tekshiruvi
        if not sale_id:
            return JsonResponse({
                'status': 'fail', 
                'message': 'Sotuv ID ko\'rsatilmagan'
            })
        
        # Sotuvni topish
        sale = get_object_or_404(models.Sale, pk=sale_id)
        
        # Agar nasiya summasi 0 bo'lsa yoki yo'q bo'lsa
        if sale.credit_amount <= 0:
            return JsonResponse({
                'status': 'fail', 
                'message': 'Bu sotuv nasiyali emas yoki allaqachon to\'langan'
            })
        
        # Nasiya summasini naqd to'lovga o'tkazish
        sale.cash_amount += sale.credit_amount
        sale.credit_amount = 0
        sale.client_due_date = None  # To'lov muddatini o'chirish
        sale.save()
        
        return JsonResponse({
            'status': 'ok', 
            'message': 'Sotuv muvaffaqiyatli to\'landi deb belgilandi',
            'sale_id': sale.id,
            'new_cash_amount': sale.cash_amount,
            'new_credit_amount': sale.credit_amount
        })
        
    except models.Sale.DoesNotExist:
        return JsonResponse({
            'status': 'fail', 
            'message': 'Sotuv topilmadi'
        })
        
    except ValueError as e:
        return JsonResponse({
            'status': 'fail', 
            'message': 'Noto\'g\'ri ma\'lumotlar yuborildi'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'fail', 
            'message': f'Xatolik yuz berdi: {str(e)}'
        })
@require_POST
def make_payment(request):
    sale_id = request.POST.get('sale_id')
    payment_amount = float(request.POST.get('payment_amount'))
    
    try:
        sale = models.Sale.objects.get(id=sale_id)
        
        if payment_amount > sale.credit_amount:
            return JsonResponse({
                'status': 'error', 
                'message': 'To\'lov summasi nasiya summasidan oshib ketdi'
            })
        
        # Nasiyani kamaytirish
        sale.credit_amount -= payment_amount
        
        # Agar nasiya 0 bo'lsa, to'liq to'langan deb belgilash
        if sale.credit_amount <= 0:
            sale.credit_amount = 0
            sale.is_paid = True  # Agar bunday maydon bo'lsa
        
        sale.save()
        
        return JsonResponse({
            'status': 'ok',
            'remaining_credit': sale.credit_amount,
            'message': 'To\'lov muvaffaqiyatli qilindi'
        })
        
    except models.Sale.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Sotuv topilmadi'
        })
def search_sales_ajax(request):
    sale_id = request.GET.get('sale_id', '').strip()
    date = request.GET.get('date', '').strip()
    client_name = request.GET.get('client_name', '').strip()
    
    sales = models.Sale.objects.select_related('seller').all()
    
    # Filtrlar
    if sale_id:
        try:
            sales = sales.filter(id=int(sale_id))
        except ValueError:
            return JsonResponse({'results': []})
    
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            sales = sales.filter(date__date=date_obj)
        except ValueError:
            pass
    
    if client_name:
        sales = sales.filter(
            Q(client_full_name__icontains=client_name)
        )
    
    results = []
    for sale in sales[:20]:  
        results.append({
            'id': sale.id,
            'date': sale.date.strftime('%Y-%m-%d %H:%M'),
            'client_name': sale.client_full_name or 'Naqd mijoz',
            'total_amount': sale.total_price,
            'seller_name': sale.seller.name if sale.seller else 'Noma\'lum'
        })
    
    return JsonResponse({'results': results})


def sale_details_ajax(request, pk):
    try:
        sale = models.Sale.objects.prefetch_related('items__product').select_related('seller').get(id=pk)
        
        sale_data = {
            'id': sale.id,
            'date': sale.date.strftime('%Y-%m-%d %H:%M'),
            'client_name': sale.client_full_name or 'Naqd mijoz',
            'client_phone': sale.client_phone,
            'total_amount': sale.total_price,
            'seller_name': sale.seller.name if sale.seller else 'Noma\'lum',
            'items': []
        }
        
        for item in sale.items.all():
            sale_data['items'].append({
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.price,
                'discount': item.discount,
                'total_price': item.total
            })
        
        return JsonResponse({'status': 'ok', 'sale': sale_data})
    
    except models.Sale.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sotuv topilmadi'})


from django.views.decorators.http import require_http_methods
from .models import Category, SubCategory

def categories_page(request):
    return render(request, 'in-and-out/create.html')

def add_category_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        if name and type:
            Category.objects.create(name=name, type=type)
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'fail', 'message': 'Maʼlumot yetarli emas'})

def add_subcategory_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        if name and category_id:
            try:
                category = Category.objects.get(id=category_id)
                SubCategory.objects.create(name=name, category=category)
                return JsonResponse({'status': 'ok'})
            except Category.DoesNotExist:
                return JsonResponse({'status': 'fail', 'message': 'Kategoriya topilmadi'})
    return JsonResponse({'status': 'fail', 'message': 'Maʼlumot yetarli emas'})

def category_list_api(request):
    data = []
    for cat in Category.objects.all():
        subcats = cat.subcategories.all().values('id', 'name')
        data.append({
            'id': cat.id,
            'name': cat.name,
            'type': cat.type,
            'subcategories': list(subcats)
        })
    return JsonResponse(data, safe=False)

# ✅ Yangi delete funksiyalari
@require_http_methods(["DELETE"])
def delete_category_ajax(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id)
        category_name = category.name
        
        # Kategoriya o'chirilganda barcha subkategoriyalar ham o'chadi (CASCADE)
        category.delete()
        
        return JsonResponse({
            'status': 'ok', 
            'message': f'"{category_name}" kategoriyasi muvaffaqiyatli o\'chirildi'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'fail', 
            'message': f'Kategoriyani o\'chirishda xato: {str(e)}'
        })

@require_http_methods(["DELETE"])
def delete_subcategory_ajax(request, subcategory_id):
    try:
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        subcategory_name = subcategory.name
        
        subcategory.delete()
        
        return JsonResponse({
            'status': 'ok', 
            'message': f'"{subcategory_name}" turkumi muvaffaqiyatli o\'chirildi'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'fail', 
            'message': f'Turkumni o\'chirishda xato: {str(e)}'
        })
"""

 

