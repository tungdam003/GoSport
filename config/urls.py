
from django.contrib import admin
from django.urls import path, include
from booking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    path('uu-dai/', views.promotions, name='promotions'),
]
