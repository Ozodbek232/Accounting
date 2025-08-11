from django.db import models
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from django.db.models import Sum
from abc import  abstractmethod
class CustomUser(Abst)
class Seller(models.Model):
    image = ResizedImageField(_("Maxsulot rasmi"), size=[60, 60], quality=99, crop=["middle", "center"], null=True, blank=True, upload_to="seller/%Y/%m",)
    first_name = models.CharField(_("Ismi"), max_length=40)
    last_name = models.CharField(_("Familyasi"), max_length=40)
    phone_number = models.IntegerField(_("Telefon raqami"))
    
    class Meta:
        db_table = "Seller"
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
    
    def __str__(self):
        return f"{self.first_name}"

class ProductCategory(models.Model):
    title = models.CharField(_("Firma nomi"), max_length=256)
    
    class Meta:
        db_table = "product_category"
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")
    
    def __str__(self):
        return f"{self.title}"

class Product(models.Model):
    image = ResizedImageField(_("Maxsulot rasmi"), size=[40, 40], quality=99, crop=["middle", "center"], upload_to="slider/%Y/%m",)
    name = models.CharField(_("Nomi"), max_length=256)
    category = models.ForeignKey(ProductCategory, verbose_name="Maxsulot firmasi", on_delete=models.CASCADE, related_name="products")
    entry_price = models.IntegerField("Tan narxi") 
    price = models.IntegerField(_("Narxi"))
    max_discount = models.IntegerField(_("maksimal chagirma"))
    amount = models.IntegerField(_("Miqdori"))
    date_published = models.DateField(_("Sanasi"))
    
    class Meta:
        db_table = "product"
        verbose_name = _("product")
        verbose_name_plural = _("products")
    
    def __str__(self):
        return f"{self.name}"

# models.py - Yangilangan modellar

# models.py - Yangilangan modellar

from django.db import models
from django.db.models import Sum

class Sale(models.Model):
    SALE_STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('paid', 'To\'langan'),
        ('partial', 'Qisman to\'langan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    client_full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mijoz ismi")
    client_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon raqami")
    client_due_date = models.DateField(blank=True, null=True, verbose_name="To'lov muddati")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    total_price = models.IntegerField(default=0, verbose_name="Umumiy narx")
    paid_amount = models.IntegerField(default=0, verbose_name="To'langan summa")
    pending_amount = models.IntegerField(default=0, verbose_name="Kutilayotgan to'lov")
    remaining_amount = models.IntegerField(default=0, verbose_name="Qolgan qarz")
    status = models.CharField(max_length=20, choices=SALE_STATUS_CHOICES, default='pending', verbose_name="Status")
    
    class Meta:
        verbose_name = "Sotuv"
        verbose_name_plural = "Sotuvlar"
        ordering = ['-date']
    
    def __str__(self):
        return f"Sotuv #{self.id} - {self.date.strftime('%d.%m.%Y %H:%M')}"
    
    def update_totals(self):
        """Sotuv umumiy summasini va to'lovlarni yangilash"""
        # SaleItem'lardan umumiy narxni hisoblash
        total = self.items.aggregate(total_sum=Sum('total'))['total_sum'] or 0
        self.total_price = total
        
        # To'langan summa hisobi
        total_paid = self.payments.aggregate(total_paid=Sum('amount'))['total_paid'] or 0
        self.paid_amount = total_paid
        
        # Kutilayotgan to'lov va qarz hisobi
        self.pending_amount = max(self.total_price - self.paid_amount, 0)
        self.remaining_amount = self.pending_amount  # Qarz = kutilayotgan to'lov
        
        # Status yangilash
        if self.pending_amount == 0 and self.total_price > 0:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        
        self.save()

   
    @property
    def calculated_total_price(self):
        """Hisoblangan umumiy narx"""
        return self.items.aggregate(total_sum=Sum('total'))['total_sum'] or 0
    
    @property
    def is_fully_paid(self):
        """To'liq to'langanligini tekshirish"""
        return self.remaining_amount == 0
    
    @property
    def is_overdue(self):
        """Muddati o'tganligini tekshirish"""
        from django.utils import timezone
        if self.client_due_date and self.status in ['pending', 'partial']:
            return self.client_due_date < timezone.now().date()
        return False

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name="Sotuv")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Mahsulot")
    quantity = models.IntegerField(verbose_name="Miqdor")
    price = models.IntegerField(verbose_name="Narx")
    discount = models.IntegerField(default=0, verbose_name="Chegirma")
    total = models.IntegerField(blank=True, null=True, verbose_name="Jami")
    
    class Meta:
        verbose_name = "Sotuv mahsuloti"
        verbose_name_plural = "Sotuv mahsulotlari"
    
    def save(self, *args, **kwargs):
        # Jami narxni hisoblash (narx - chegirma) * miqdor
        self.total = (self.price - self.discount) * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} dona"

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('cash', 'Naqd'),
        ('card', 'Karta'),
        ('credit', 'Nasiya'),
        ('bank_transfer', 'Bank o\'tkazmasi'),
    ]
    
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments', verbose_name="Sotuv")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, verbose_name="To'lov turi")
    amount = models.IntegerField(verbose_name="Summa")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Sana")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    
    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.amount:,} UZS"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sale ni yangilash
        self.sale.update_totals()




