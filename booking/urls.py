
from django.urls import path
from . import views
path('book/<int:court_id>/', views.book_court, name='book_court'),

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
  
    path('book/<int:court_id>/', views.book_court, name='book_court'),

    path('booking-history/', views.booking_history, name='booking_history'),

    path(
    'cancel-booking/<int:booking_id>/',
    views.cancel_booking,
    name='cancel_booking'
),


]
