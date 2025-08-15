from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.utils import timezone
from common import models, forms

from helpers.views import CreateView, UpdateView, DeleteView
from datetime import date
import json
import datetime
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return self.redirect_by_role(request.user)
        return render(request, "signin.html")

    def post(self, request):
        req = request.POST.dict()
        username = req.get("username")
        password = req.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return self.redirect_by_role(user)
        else:
            return render(request, "signin.html", {"error": True})

    def redirect_by_role(self, user):
        if user.role == "manager":
            return HttpResponseRedirect(reverse_lazy("common:home"))
        if user.role == "cashier":
            return HttpResponseRedirect(reverse_lazy("common:home"))
        if user.role == "seller":
            return HttpResponseRedirect(reverse_lazy("common:home"))

        raise PermissionDenied("You don't have access to this page")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse_lazy("login"))


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

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Sale
from decimal import Decimal

# YANGI FUNKSIYA: Nasiyali sotuvlarni ko'rish
def credit_sale(request):
    credit_sales = models.Payment.objects.filter(
        payment_type='credit'
    ).prefetch_related('sale__items__product').select_related('sale').order_by('-date')
    
    # Statistika hisoblash
    total_credit = 0
    total_cash = 0
    total = 0
    
    for payment in credit_sales:

        sale = payment.sale
        total_credit += sale.pending_amount  # Qolgan qarz
        total_cash += sale.paid_amount       # To'langan summa
        total += sale.total_price           # Jami summa
    
    context = {
        'credit_sales': credit_sales,
        'total_credit': total_credit,
        'total_cash': total_cash,
        'total': total
    }
    
    return render(request, 'manager/sale/credit-payment.html', context)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging

# Logger qo'shish
logger = logging.getLogger(__name__)

@csrf_exempt  # Agar CSRF muammosi bo'lsa
@require_POST
def make_payment(request, sale_id):
    try:
        sale_id = request.POST.get('sale_id')
        payment_amount = request.POST.get('payment_amount')
        
       
        # Ma'lumotlar tekshiruvi
        if not sale_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Sale ID topilmadi'
            })
            
        if not payment_amount:
            return JsonResponse({
                'status': 'error', 
                'message': 'To\'lov summasi ko\'rsatilmagan'
            })
        
        # Sonlarni convert qilish
        try:
            payment_amount = int(float(payment_amount))
            sale_id = int(sale_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'status': 'error',
                'message': 'Noto\'g\'ri ma\'lumot formati'
            })
        
        # Sale obyektini olish
        try:
            from .models import Sale, Payment  # Sizning models.py dan import qiling
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Sotuv topilmadi'
            })
        
        # To'lov summasini tekshirish
        if payment_amount <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'To\'lov summasi 0 dan katta bo\'lishi kerak'
            })
        
        # Sale ma'lumotlarini yangilash

        sale.update_totals()
        sale.refresh_from_db()
        
       
        # Nasiya summasini tekshirish (credit to'lov turi bo'yicha)
        current_credit = sale.credit_amount
        max_credit_payment = sale.total_price - sale.paid_amount + current_credit
        
        # Agar nasiya mavjud bo'lmasa
        if current_credit <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Bu sotuvda nasiya mavjud emas'
            })
        
        # Agar nasiya allaqachon to'langan bo'lsa  
        if sale.status == 'paid':
            return JsonResponse({
                'status': 'error',
                'message': 'Bu nasiya allaqachon to\'liq to\'langan'
            })
        
        # To'lov summasini nasiya miqdori bilan cheklash
        if payment_amount > current_credit:
            return JsonResponse({
                'status': 'error',
                'message': f'To\'lov summasi nasiya summasidan ({current_credit:,} so\'m) ko\'p bo\'lishi mumkin emas'
            })
        
        # Nasiyaning credit to'lov turini cash ga o'tkazish (nasiya to'lovi)
        # Avval credit to'lovlarni topish
        credit_payments = Payment.objects.filter(sale=sale, payment_type='credit')
        
        if not credit_payments.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Bu sotuvda nasiya to\'lovi topilmadi'
            })
        
        # Eng oxirgi credit to'lovni cash ga o'zgartirish yoki yangi cash to'lov yaratish
        # Eng oddiy usul: yangi cash to'lov qo'shish
        payment = Payment.objects.create(
            sale=sale,
            payment_type='cash',  # Nasiya to'lovi cash sifatida
            amount=payment_amount,
            description=f'Nasiya to\'lovi: {payment_amount:,} so\'m'
        )
        
        # Agar nasiya to'liq to'langan bo'lsa, credit to'lovni cash ga o'zgartirish
        sale.update_totals()
        sale.refresh_from_db()
        remaining_credit_after_payment = sale.credit_amount
        
        
        # Javobni tayyorlash
        is_fully_paid = sale.is_fully_paid
        remaining_credit = sale.credit_amount  # Nasiya qolgan qismi
        
        return JsonResponse({
            'status': 'ok',
            'remaining_credit': remaining_credit,
            'paid_amount': sale.paid_amount,
            'total_amount': sale.total_price,
            'is_paid': is_fully_paid,
            'sale_status': sale.status,
            'credit_amount': sale.credit_amount,
            'message': 'Nasiya to\'lovi muvaffaqiyatli qilindi'
        })
        
    except Exception as e:
       
        # Debug rejimida batafsil xatolik
        try:
            from django.conf import settings
            if settings.DEBUG:
                import traceback
        except:
            pass
        
        return JsonResponse({
            'status': 'error',
            'message': f'Server xatoligi: {str(e)}'
        })
# common/views.py
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from decimal import Decimal
import json

@csrf_exempt
def add_payment(request, sale_id):
    """To'lov qo'shish va kassaga ulash"""
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri metod'}, status=400)

    try:
        sale = get_object_or_404(Sale, pk=sale_id)
        data = json.loads(request.body)

        payment_type = data.get('payment_type')
        amount = Decimal(data.get('amount', 0))
        description = data.get('description', '')

        # Validatsiya
        if not payment_type:
            return JsonResponse({'status': 'error', 'message': 'To\'lov turini tanlang'}, status=400)
            
        if amount <= 0:
            return JsonResponse({'status': 'error', 'message': 'Summani kiriting'}, status=400)

        # Maksimal to'lov summasi tekshiruvi
        max_payment = sale.total_price - sale.paid_amount
        if amount > max_payment:
            return JsonResponse({
                'status': 'error', 
                'message': f'Maksimal to\'lov summasi: {max_payment:,} so\'m'
            }, status=400)

        with transaction.atomic():
            # Foydalanuvchining ochiq kassasini topish
            cash_register = CashRegister.objects.filter(
                user=request.user,
                closed_at__isnull=True
            ).order_by('-opened_at').first()

            if not cash_register:
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Sizda ochiq kassa topilmadi. Avval kassani oching'
                }, status=400)

            # Agar sale hali kassaga bog'lanmagan bo'lsa, bog'lash
            if not sale.cash_register:
                sale.cash_register = cash_register
                sale.save()

            # To'lov yaratish
            payment = Payment.objects.create(
                sale=sale,
                payment_type=payment_type,
                amount=amount,
                description=description or f'{dict(Payment.PAYMENT_TYPE_CHOICES)[payment_type]} to\'lovi'
            )

            # Sotuv summasini yangilash (Payment.save() da avtomatik chaqiriladi)
            sale.refresh_from_db()

            # Kassaga qo'shish — faqat paid bo'lganda va cash/card bo'lsa
            if sale.status == 'paid' and payment_type in ['cash', 'card']:
                cash_register.add_payment(payment)

        return JsonResponse({
            'status': 'success',
            'message': 'To\'lov muvaffaqiyatli qo\'shildi',
            'data': {
                'sale_id': sale.id,
                'sale_status': sale.status,
                'paid_amount': sale.paid_amount,
                'pending_amount': sale.pending_amount,
                'is_fully_paid': sale.is_fully_paid,
                'payment_id': payment.id,
                'cash_register_id': cash_register.id if cash_register else None
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Noto\'g\'ri JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Server xatoligi: {str(e)}'}, status=500)


@csrf_exempt
@require_POST
def mark_sale_as_paid(request):
    """Sotuvni to'liq to'langan deb belgilash"""
    try:
        sale_id = request.POST.get('sale_id')
        
        if not sale_id:
            return JsonResponse({
                'status': 'error', 
                'message': 'Sotuv ID ko\'rsatilmagan'
            })
        
        sale = get_object_or_404(Sale, pk=sale_id)
        sale.update_totals()
        
        
        # Agar qarz yo'q bo'lsa
        if sale.pending_amount <= 0:
            return JsonResponse({
                'status': 'error', 
                'message': 'Bu sotuv allaqachon to\'langan'
            })
        
        # Qolgan summa uchun cash to'lov yaratish
        Payment.objects.create(
            sale=sale,
            payment_type='cash',
            amount=sale.pending_amount,
            description='To\'liq to\'lov (avtomatik)'
        )
        
        # Sale avtomatik yangilanadi
        sale.refresh_from_db()
        
        return JsonResponse({
            'status': 'ok', 
            'message': 'Sotuv muvaffaqiyatli to\'liq to\'langan deb belgilandi',
            'sale_id': sale.id,
            'paid_amount': sale.paid_amount,
            'pending_amount': sale.pending_amount,
            'sale_status': sale.status
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Xatolik yuz berdi: {str(e)}'
        })


@csrf_exempt
def save_sale(request):
    """Yangi sotuv saqlash"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cart_items = data.get('cart_items', {})
            payment_data = data.get('payment', {})
            
            
            if not cart_items:
                return JsonResponse({'status': 'error', 'message': 'Korzina bo\'sh'}, status=400)
            
            # Yangi sotuv yaratish
            from common.models import Sale, Product, SaleItem, Payment
            sale = Sale.objects.create(
                user=request.user,
                status='pending',
                total_price=0,
                paid_amount=0,
                pending_amount=0,
                remaining_amount=0
            )
            
            total_amount = 0
            
            # Sale items yaratish
            for product_id, item_data in cart_items.items():
                try:
                    product = Product.objects.get(id=product_id)
                    quantity = int(item_data['quantity'])
                    discount_per_item = float(item_data.get('discount', 0))
                    
                    # Mavjudlik tekshiruvi
                    if product.amount < quantity:
                        sale.delete()  # Xatolik bo'lsa sotuvni o'chirish
                        return JsonResponse({
                            'status': 'error', 
                            'message': f'{product.name} - mavjud: {product.amount}, so\'ralgan: {quantity}'
                        }, status=400)
                    
                    # Sale item yaratish
                    sale_item = SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        discount=discount_per_item
                        # total avtomatik hisoblanadi
                    )
                    
                    total_amount += sale_item.total
                    
                    # Mahsulot miqdorini kamaytirish
                    product.amount -= quantity
                    product.save()
                    
                except Product.DoesNotExist:
                    sale.delete()
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Mahsulot topilmadi: ID {product_id}'
                    }, status=404)
            
            # Sale umumiy summasini yangilash
            sale.total_price = total_amount
            sale.pending_amount = total_amount
            sale.remaining_amount = total_amount
            
            # To'lov ma'lumotlari bor bo'lsa
            if payment_data and payment_data.get('payment_type'):
                payment_type = payment_data.get('payment_type')
                payment_amount = float(payment_data.get('amount', 0))
                client_name = payment_data.get('client_name', '')
                client_phone = payment_data.get('client_phone', '')
                client_due_date = payment_data.get('client_due_date', None)
                description = payment_data.get('description', '')
                
                if 0 < payment_amount <= total_amount:
                    # To'lov yaratish
                    Payment.objects.create(
                        sale=sale,
                        payment_type=payment_type,
                        amount=payment_amount,
                        description=description or f'{dict(Payment.PAYMENT_TYPE_CHOICES)[payment_type]} to\'lovi'
                    )
                    
                    # Mijoz ma'lumotlari (nasiya uchun)
                    if payment_type == 'credit':
                        sale.client_full_name = client_name
                        sale.client_phone = client_phone
                        if client_due_date:
                            from datetime import datetime
                            sale.client_due_date = datetime.strptime(client_due_date, '%Y-%m-%d').date()
            
            # Final save
            sale.save()
            # update_totals() Payment yaratilganda avtomatik chaqiriladi
            sale.refresh_from_db()
            
            
            # Javob - HTML template bilan mos keluvchi response
            return JsonResponse({
                'status': 'saved',  # HTML templateda 'saved' kutilmoqda
                'sale_id': sale.id,
                'total_amount': sale.total_price,
                'paid_amount': sale.paid_amount,
                'pending_amount': sale.pending_amount,
                'sale_status': sale.status,
                'redirect_url': '/sale/' if sale.status == 'paid' else '/pending-payments/',
                'message': 'Sotuv muvaffaqiyatli yaratildi'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Xatolik yuz berdi: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)
# Debug va qo'shimcha funksiyalar
from common.models import Sale, Payment

@csrf_exempt
def debug_sale_info(request, sale_id):
    """Debug uchun sale ma'lumotlari"""
    try:
        from common.models import Sale, Payment
        sale = Sale.objects.get(id=sale_id)
        
        # Ma'lumotlarni yangilash
        sale.update_totals()
        
        # To'lovlar
        payments = []
        for p in sale.payments.all():
            payments.append({
                'id': p.id,
                'type': p.payment_type,
                'type_display': p.get_payment_type_display(),
                'amount': p.amount,
                'date': p.date.strftime('%d.%m.%Y %H:%M'),
                'description': p.description
            })
        
        # Items
        items = []
        for item in sale.items.all():
            items.append({
                'product': str(item.product),
                'quantity': item.quantity,
                'price': item.price,
                'discount': item.discount,
                'total': item.total
            })
        
        return JsonResponse({
            'sale_id': sale.id,
            'status': sale.status,
            'total_price': sale.total_price,
            'paid_amount': sale.paid_amount,
            'pending_amount': sale.pending_amount,
            'remaining_amount': sale.remaining_amount,
            'credit_amount': sale.credit_amount,
            'cash_amount': sale.cash_amount,
            'card_amount': sale.card_amount,
            'bank_transfer_amount': sale.bank_transfer_amount,
            'is_fully_paid': sale.is_fully_paid,
            'client_name': sale.client_full_name,
            'client_phone': sale.client_phone,
            'client_due_date': sale.client_due_date.isoformat() if sale.client_due_date else None,
            'payments': payments,
            'items': items
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})

def pending_payments_view(request):
    return render(request, 'manager/sale/pending-payment.html')
def pending_payments_api(request):
    """Kutilayotgan to'lovlar API"""
    try:
        from common.models import Sale
        
        # Faqat kutilayotgan to'lovi bo'lgan sotuvlar
        sales = Sale.objects.filter(pending_amount__gt=0).order_by('-date')
        
        # Filtrlar
        status_filter = request.GET.get('status', '')
        client_filter = request.GET.get('client', '')
        date_filter = request.GET.get('date', '')
        
        if status_filter:
            sales = sales.filter(status=status_filter)
        
        if client_filter:
            sales = sales.filter(client_full_name__icontains=client_filter)
        
        if date_filter:
            from datetime import datetime
            try:
                date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
                sales = sales.filter(date__date=date_obj)
            except ValueError:
                pass
        
        data = []
        for sale in sales:
            # Ma'lumotlarni yangilash
            sale.update_totals()
            
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
                'pending_amount': sale.pending_amount,
                'credit_amount': sale.credit_amount,
                'status': sale.status,
                'payments': payments
            })
        
        return JsonResponse({'sales': data})
        
    except Exception as e:
        return JsonResponse({'error': str(e)})


def payment_statistics_api(request):
    """To'lov statistikalari"""
    try:
        from common.models import Sale, Payment
        from datetime import date
        
        today = date.today()
        
        # Jami kutilayotgan to'lovlar
        total_pending = Sale.objects.filter(
            pending_amount__gt=0
        ).aggregate(total=Sum('pending_amount'))['total'] or 0
        
        today_payments = Payment.objects.filter(date__date=today).aggregate(total=Sum('amount'))['total'] or 0
        # Status bo'yicha sanoq
        pending_count = Sale.objects.filter(status='pending').count()
        partial_count = Sale.objects.filter(status='partial').count()
        paid_count = Sale.objects.filter(status='paid').count()
        
        # Muddati o'tgan
        overdue_count = Sale.objects.filter(
            client_due_date__lt=today,
            status__in=['pending', 'partial']
        ).count()
        
        return JsonResponse({
            'total_pending': total_pending,
            'today_payments': today_payments,
            'pending_count': pending_count,
            'partial_count': partial_count,
            'paid_count': paid_count,
            'overdue_count': overdue_count
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})


@csrf_exempt  
def create_payment_modal(request, sale_id):
    """To'lov modal ma'lumotlari"""
    if request.method == "GET":
        try:
            from common.models import Sale, Payment
            sale = get_object_or_404(Sale, pk=sale_id)
            
            sale.update_totals()
            
            return JsonResponse({
                'status': 'success',
                'sale': {
                    'id': sale.id,
                    'date': sale.date.strftime('%d.%m.%Y %H:%M'),
                    'total_price': sale.total_price,
                    'paid_amount': sale.paid_amount,
                    'pending_amount': sale.pending_amount,
                    'credit_amount': sale.credit_amount,
                    'client_name': sale.client_full_name or '',
                    'client_phone': sale.client_phone or '',
                    'client_due_date': sale.client_due_date.isoformat() if sale.client_due_date else '',
                    'status': sale.status,
                    'user': sale.user.username if sale.user else '',    # 🔹 loginda ishlatadigan username
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
def sale(request):
    return render(request, 'manager/sale/create.html')

class SaleListView(ListView):
    model = models.Sale
    template_name = 'manager/sale/list.html'
    context_object_name = 'objects'
    queryset = models.Sale.objects.filter(status='paid')
    
    def get_queryset(self):
        object_list = self.queryset
        return object_list
    
    def get_context_data(self, **kwargs):
        sold_products = models.SaleItem.objects.select_related('product', 'sale').filter(
            sale__status='paid'
        )
     
        context = super().get_context_data(**kwargs)
        total = self.queryset.aggregate(total_price=Sum('total_price'))['total_price'] or 0
        count = self.queryset.count()
        
        today = datetime.date.today()

        monthly_sales = models.Sale.objects.filter(
            status='paid',
            date__month= today.month
        )
        monthly_count = monthly_sales.count()
        context['sold_products'] = sold_products
        context['monthly_count'] = monthly_count
        context['count'] = count
        context['total_price'] = total
        return context

def sale_details_ajax(request, sale_id):
    try:
        # Avval Sale obyektini topamiz
        sale = models.Sale.objects.prefetch_related('items__product').get(pk=sale_id)
        
        # Credit Payment bor yoki yo'qligini tekshiramiz
        has_credit_payment = models.Payment.objects.filter(
            sale=sale, 
            payment_type='credit'
        ).exists()
        
        if not has_credit_payment:
            return JsonResponse({'status': 'error', 'message': 'Bu sotuv nasiyali emas'})
        
        sale_data = {
            'id': sale.id,
            'date': sale.date.strftime('%Y-%m-%d %H:%M'),
            'client_name': sale.client_full_name or 'Noma\'lum mijoz',
            'client_phone': sale.client_phone,
            'total_amount': sale.total_price,
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
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Xatolik: {str(e)}'})

class CustomUserListView(ListView):
    model = models.CustomUser
    template_name = "manager/custom_user/list.html"

    context_object_name = "objects"
    queryset = models.CustomUser.objects.filter(is_superuser=False).order_by("-id")
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role"] = True
        return context

    def get_queryset(self):
        object_list = self.queryset
        search = self.request.GET.get("search", None)
        role = self.request.GET.get("role", None)
        is_active = self.request.GET.get("user_status", None)
        if search:
            object_list = object_list.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(username__icontains=search)
            )
        if role:
            object_list = object_list.filter(role=role)
        if is_active == "active":
            object_list = object_list.filter(is_active=True)
        if is_active == "inactive":
            object_list = object_list.filter(is_active=False)
        return object_list


class CustomUserCreateView(CreateView):

    model = models.CustomUser
    form_class = forms.CustomUserForm
    template_name = "manager/custom_user/create.html"
    context_object_name = "object"
    success_url = "common:user-list"
    success_create_url = "common:user-create"


class CustomUserUpdateView(UpdateView):

    model = models.CustomUser
    form_class = forms.CustomUserForm
    template_name = "manager/custom_user/update.html"
    context_object_name = "object"
    success_url = "common:user-list"
    success_update_url = "common:user-update"


class CustomUserInfoUpdateView(UpdateView):
    model = models.CustomUser
    form_class = forms.CustomUserInfoForm
    template_name = "manager/custom_user/info.html"
    context_object_name = "object"
    success_url = "common:user-list"


class CustomUserDeleteView(DeleteView):
    model = models.CustomUser
    success_url = "common:user-list"


class CustomUserView(View):
    def get(self, request, pk):
        return render(request, "manager/custom_user/info.html")

    def post(self, request, pk):
        user = get_object_or_404(models.CustomUser, pk=pk)
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        user.first_name, user.last_name, user.username, user.phone, user.email = (
            first_name,
            last_name,
            username,
            phone,
            email,
        )
        user.save()

        return redirect("common:home")
# views.py
from .models import CashRegister
class CashRegisterListView(ListView):
    model = models.CashRegister
    template_name = "manager/cash/list.html"

    context_object_name = "objects"
    queryset = model.objects.all().order_by("-id")
    paginate_by = 10

    def get_queryset(self):
        object_list = self.queryset
        search = self.request.GET.get("search", None)
        if search:
            object_list = object_list.filter(Q(title__icontains=search))

        return object_list


class CashRegisterCreateView(CreateView):
    model = models.CashRegister
    form_class = forms.CashRegisterForm
    template_name = "manager/cash/create.html"
    context_object_name = "object"
    success_url = "common:cash-list"
    success_create_url = "common:cash-create"


from django.http import JsonResponse

class CashRegisterDeleteView(DeleteView):
    model = models.CashRegister
    success_url = "common:cash-list"


# views.py - CashRegisterUpdateView ni yangilang
class CashRegisterUpdateView(UpdateView):
    model = CashRegister
    form_class = forms.CashRegisterForm
    template_name = "manager/cash/update.html"
    context_object_name = "object"
    success_url = "common:cash-list"
    success_update_url = "common:cash-update"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        try:
            # Reset metodini chaqirish
            result = self.object.reset_register()
            
            return redirect("common:cash-list")            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Xatolik yuz berdi: {str(e)}'
            }, status=500)


# Alohida reset view
@csrf_exempt
def reset_cash_register(request, register_id):
    """Kassa reset qilish - faqat sotuvlarni o'chirish"""
    if request.method == "POST":
        try:
            from django.shortcuts import get_object_or_404
            from django.db import transaction
            from common.models import CashRegister
            
            cash_register = get_object_or_404(CashRegister, pk=register_id)
            
            # Faqat kassa egasi yoki admin reset qila oladi
            if request.user != cash_register.user and not request.user.is_superuser:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Sizda bu kassani reset qilish huquqi yo\'q'
                }, status=403)
            
            # Reset qilish (mahsulotlar qaytarilmaydi!)
            result = cash_register.reset_register()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Kassa #{cash_register.id} muvaffaqiyatli reset qilindi! Sotuvlar o\'chirildi, mahsulotlar ochib ketdi.',
                'details': {
                    'reset_count': result['reset_count'],
                    'cash_register_id': cash_register.id,
                    'user': cash_register.user.username,
                    'reset_time': cash_register.opened_at.strftime('%d.%m.%Y %H:%M')
                },
                'deleted_sales': result['deleted_sales'][:10]  # Birinchi 10 tani ko'rsatish
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'status': 'error',
                'message': f'Server xatoligi: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Faqat POST so\'rov qabul qilinadi'
    }, status=400)


# Bonus: Kassani yopish funksiyasi
@csrf_exempt
def close_cash_register(request, register_id):
    """Kassani yopish (reset qilmasdan)"""
    if request.method == "POST":
        try:
            cash_register = get_object_or_404(CashRegister, pk=register_id)
            
            if request.user != cash_register.user and not request.user.is_superuser:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Sizda bu kassani yopish huquqi yo\'q'
                }, status=403)
            
            if cash_register.closed_at:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bu kassa allaqachon yopilgan'
                }, status=400)
            
            # Kassani yopish (ma'lumotlar saqlanadi)
            from django.utils import timezone
            cash_register.closed_at = timezone.now()
            cash_register.save()
            
            # Statistika
            sales_count = cash_register.cash.filter(status='paid').count()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Kassa #{cash_register.id} yopildi',
                'details': {
                    'total_cash': cash_register.total_cash,
                    'total_card': cash_register.total_card,
                    'total_sales': cash_register.total_sales,
                    'sales_count': sales_count,
                    'opened_at': cash_register.opened_at.strftime('%d.%m.%Y %H:%M'),
                    'closed_at': cash_register.closed_at.strftime('%d.%m.%Y %H:%M')
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CashFlowForm
from .models import CashFlow, CashRegister
from django.shortcuts import render, redirect
from .models import CashFlow, CashRegister
from .forms import CashFlowForm
from django.db.models import Sum
from django.contrib import messages

def add_cashflow(request):
    # Ochiq kassani olish
    cash_register = CashRegister.objects.filter(closed_at__isnull=True).first()

    if request.method == "POST":
        form = CashFlowForm(request.POST)
        if form.is_valid():
            cashflow = form.save(commit=False)
            cashflow.cash_register = cash_register  # hozirgi kassa
            cashflow.save()

            # Kassani yangilash
            if cashflow.flow_type == 'income':
                cash_register.total_cash += cashflow.amount
            elif cashflow.flow_type == 'expense':
                cash_register.total_cash -= cashflow.amount
            cash_register.save()

            messages.success(request, "Tranzaksiya qo‘shildi!")
            return redirect('common:add_cashflow')
    else:
        form = CashFlowForm()

    # Tranzaksiyalar ro‘yxati
    transactions = CashFlow.objects.filter(cash_register=cash_register).order_by('-created_at')

    # Hisob-kitoblar
    total_cash = cash_register.total_cash if cash_register else 0
    daily_income = transactions.filter(flow_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    daily_expense = transactions.filter(flow_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'form': form,
        'transactions': transactions,
        'total_cash': total_cash,
        'daily_income': daily_income,
        'daily_expense': daily_expense,
    }

    return render(request, 'manager/in-out/create.html', context)

