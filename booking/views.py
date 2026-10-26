
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Sport, Court, TimeSlot, Booking
from django.db.models import Q # Nhớ import Q nếu chưa có

def home(request):
    sports = Sport.objects.all()
    query = request.GET.get('q', '').strip()
    
    # Lọc sân theo từ khóa tìm kiếm (tên sân hoặc địa điểm hoặc tên môn thể thao)
    if query:
        courts = Court.objects.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query) |
            Q(sport__name__icontains=query)
        )
    else:
        courts = Court.objects.all()

    return render(request, 'booking/home.html', {
        'sports': sports,
        'courts': courts,
        'query': query,
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
        elif password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
        else:
            User.objects.create_user(
                username=username,
                password=password
            )
            messages.success(
                request, 'Đăng ký thành công. Hãy đăng nhập.'
            )
            return redirect('user_login')

    return render(request, 'booking/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.error(
            request, 'Tên đăng nhập hoặc mật khẩu không đúng.'
        )

    return render(request, 'booking/login.html')


def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

    return redirect('home')



@login_required(login_url='user_login')
def book_court(request, court_id):
    court = get_object_or_404(Court, id=court_id)
    today_str = timezone.localdate().strftime('%Y-%m-%d')
    selected_date_str = request.GET.get('booking_date') or today_str

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        selected_date = timezone.localdate()
        selected_date_str = today_str

    if request.method == 'POST':
        time_slot_id = request.POST.get('time_slot')
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        payment_method = request.POST.get('payment_method')

        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            
            # Kiểm tra ràng buộc Khung giờ vàng (17h - 21h) không cho chọn tiền mặt nếu muốn
            # (Giả sử chuỗi time_slot có dạng "17:00 - 18:00" hoặc lấy giờ bắt đầu)
            slot_start_hour = int(str(time_slot).split(':')[0])
            is_golden_hour = (17 <= slot_start_hour < 21)

            if is_golden_hour and payment_method == 'CASH':
                messages.error(request, 'Khung giờ vàng (17h - 21h) tuyệt đối không hỗ trợ thanh toán tiền mặt để tránh bùng sân. Vui lòng chọn chuyển khoản!')
                return redirect('book_court', court_id=court.id)

            if selected_date < timezone.localdate():
                messages.error(request, 'Không thể đặt sân trong quá khứ.')

            elif Booking.objects.filter(
                 court=court,
                 booking_date=selected_date,
                 time_slot=time_slot
                ).exclude(status='CANCELLED').exists():
                 messages.error(request, 'Khung giờ này đã có người đặt.')

            else:
                Booking.objects.create(
                    user=request.user,
                    court=court,
                    time_slot=time_slot,
                    booking_date=selected_date,
                    full_name=full_name,
                    phone_number=phone_number,
                    payment_method=payment_method,
                    status='CONFIRMED'
                )
                messages.success(request, 'Đặt sân thành công! Vui lòng đọc kỹ chính sách hủy sân.')
                return redirect('booking_history')

        except (ValueError, TimeSlot.DoesNotExist):
            messages.error(request, 'Thông tin đặt sân không hợp lệ.')

    booked_slot_ids = Booking.objects.filter(
        court=court,
        booking_date=selected_date
    ).exclude(status='CANCELLED').values_list('time_slot_id', flat=True)

    available_time_slots = TimeSlot.objects.exclude(id__in=booked_slot_ids)

    return render(request, 'booking/book_court.html', {
        'court': court,
        'time_slots': available_time_slots,
        'today': today_str,
        'selected_date': selected_date_str,
    })

@login_required(login_url='user_login')
def booking_history(request):
    bookings = Booking.objects.filter(
        user=request.user
    ).select_related(
        'court', 'court__sport', 'time_slot'
    ).order_by('-booking_date')

    return render(request, 'booking/booking_history.html', {
        'bookings': bookings,
    })


@login_required(login_url='user_login')
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return redirect('booking_history')

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'CONFIRMED':
        booking.status = 'CANCELLED'
        booking.save()
        messages.success(request, 'Đã hủy đặt sân thành công.')
    else:
        messages.error(request, 'Lịch đặt này đã được hủy hoặc xử lý.')

    return redirect('booking_history')

def promotions(request):
    return render(request, 'booking/promotions.html')