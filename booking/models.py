from django.db import models


class Sport(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    
from django.db import models

class Court(models.Model):
    sport = models.ForeignKey(
        Sport,
        on_delete=models.CASCADE,
        related_name='courts'
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='ACTIVE')

    def __str__(self):
        return self.name

    @property
    def formatted_price(self):
        # Chuyển số tiền thành kiểu int, định dạng dấu phẩy rồi thay bằng dấu chấm (VD: 50,000 -> 50.000)
        return f"{int(self.price):,}".replace(",", ".")

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


from django.contrib.auth.models import User


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"




class Booking(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Tiền mặt (Thanh toán tại sân)'),
        ('BANK', 'Chuyển khoản ngân hàng'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    booking_date = models.DateField()
    
    # Thông tin người đặt bổ sung
    full_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Thanh toán & Chính sách
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    status = models.CharField(max_length=20, default='CONFIRMED') # CONFIRMED, CANCELLED, BANNED
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.court.name} ({self.booking_date})"