from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser
from django.contrib import messages
import pandas as pd
from .forms import ExcelUploadForm
from .models import DataSheet
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db.models import Max
from django.core.exceptions import ValidationError


User = get_user_model()

def index(request):
    return render(request, 'main_app/index.html', {'user': request.user})

def chart(request):
    return render(request, 'main_app/chart.html', {'user': request.user})


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']

        if password != confirm_password:
            return render(request, 'main_app/register.html', {'error': 'Mật khẩu xác nhận không khớp!'})

        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return render(request, 'main_app/register.html', {'error': 'Username hoặc Email đã tồn tại!'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return redirect('login')
    else:
        return render(request, 'main_app/register.html')
    
def login_view(request):
    if request.method == 'POST':
        credential = request.POST['credential']
        password = request.POST['password']

        user = authenticate(request, username=credential, password=password)
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=credential)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'main_app/login.html', {'error': 'Thông tin đăng nhập không chính xác'})
    else:
        return render(request, 'main_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def user_info(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        user = request.user
        user.email = email
        if password and password == confirm_password:
            user.set_password(password)
        user.save()
        return redirect('user_info')
    else:
        return render(request, 'main_app/user_info.html', {'user': request.user})

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden('Bạn không có quyền truy cập trang này.')
    return wrapper

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def daily_management(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # Lưu file tạm thời
            fs = FileSystemStorage()
            filename = fs.save(excel_file.name, excel_file)
            file_path = fs.path(filename)

            try:
                # Đọc dữ liệu từ file Excel
                xls = pd.ExcelFile(file_path)
                
                for sheet_name in ['MACD', 'BREAK', 'MA10', 'MA20', 'MA50']:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    for index, row in df.iterrows():
                        DataSheet.objects.create(
                            sheet_name=sheet_name,
                            symbol=row['symbol'],
                            volume=row['volume'],
                            signal=row['signal'],
                            date=row['date'] if 'date' in row else timezone.now()
                        )
            finally:
                xls.close()
                fs.delete(filename)

            return redirect('daily_management')

    else:
        form = ExcelUploadForm()

    datasheets = DataSheet.objects.all().order_by('-date', 'symbol', 'volume')

    # Lấy giá trị unique cho filter
    unique_sheet_names  = DataSheet.objects.values_list('sheet_name', flat=True).distinct()
    unique_symbols = DataSheet.objects.values_list('symbol', flat=True).distinct()
    unique_volumes = DataSheet.objects.values_list('volume', flat=True).distinct()
    unique_signals = DataSheet.objects.values_list('signal', flat=True).distinct()
    unique_dates = DataSheet.objects.values_list('date', flat=True).distinct().order_by('-date')  # Sắp xếp theo thứ tự mới đến cũ

    return render(request, 'main_app/daily_management.html', {
        'form': form,
        'datasheets': datasheets,
        'unique_sheet_names' : unique_sheet_names,
        'unique_symbols': unique_symbols,
        'unique_volumes': unique_volumes,
        'unique_signals': unique_signals,
        'unique_dates': unique_dates,
    })

@user_passes_test(is_admin)
def admin_panel(request):
    users = CustomUser.objects.all()
    return render(request, 'main_app/admin_panel.html', {'users': users})

@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Xóa người dùng thành công!')
    return redirect('admin_panel')

@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Xử lý form sửa đổi người dùng
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')

        if username and email and role:
            user.username = username
            user.email = email
            user.role = role
            user.save()
            messages.success(request, 'Cập nhật người dùng thành công!')
            return redirect('admin_panel')
        else:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return render(request, 'main_app/edit_user.html', {'user': user})
    else:
        return render(request, 'main_app/edit_user.html', {'user': user})

def superuser_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated_view_func

@superuser_required
def create_admin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return render(request, 'main_app/create_admin.html')  # Nếu bạn dùng app-specific

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username đã tồn tại!')
            return render(request, 'main_app/create_admin.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã tồn tại!')
            return render(request, 'main_app/create_admin.html')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.is_superuser = True
            user.role = 'admin'
            user.save()
            messages.success(request, 'Tài khoản admin đã được tạo thành công!')
            return redirect('login')  # Thay 'admin_list' bằng tên đường dẫn bạn muốn chuyển hướng tới
        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {e}')
            return render(request, 'main_app/create_admin.html')
    else:
        return render(request, 'main_app/create_admin.html')  # Nếu bạn dùng app-specific
    

@csrf_exempt
def delete_selected_data(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            ids = body.get('ids', [])
            if ids:
                DataSheet.objects.filter(id__in=ids).delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'no_ids'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid_request'})

@csrf_exempt
def delete_all_data(request):
    if request.method == 'POST':
        DataSheet.objects.all().delete()
        return JsonResponse({'status': 'success'})


@login_required  
def signal_view(request):
    # Lấy danh sách các ngày có trong dữ liệu
    available_dates = DataSheet.objects.values_list('date', flat=True).distinct().order_by('-date')

    # Lấy ngày hiện tại từ request, nếu không có thì mặc định là ngày mới nhất
    selected_date = request.GET.get('date')
    
    if not selected_date:
        # Lấy ngày mới nhất nếu không có ngày được chọn
        latest_data = DataSheet.objects.latest('date')
        selected_date = latest_data.date.strftime('%Y-%m-%d')

    # Lọc dữ liệu theo ngày đã chọn và sắp xếp theo tên symbol
    all_data = DataSheet.objects.filter(date=selected_date).order_by('symbol')

    # Nhóm dữ liệu theo tên sheet và đếm số lượng Positive và Negative
    datasheets_by_type = {}
    for data in all_data:
        if data.sheet_name not in datasheets_by_type:
            datasheets_by_type[data.sheet_name] = {'datasheets': [], 'positive_count': 0, 'negative_count': 0}
        datasheets_by_type[data.sheet_name]['datasheets'].append(data)
        
        if data.signal == 'POS':
            datasheets_by_type[data.sheet_name]['positive_count'] += 1
        elif data.signal == 'NEG':
            datasheets_by_type[data.sheet_name]['negative_count'] += 1

    # Sắp xếp theo thứ tự ưu tiên các sheet
    sorted_order = ['MACD', 'BREAK', 'MA10', 'MA20', 'MA50']
    sorted_datasheets_by_type = {key: datasheets_by_type[key] for key in sorted_order if key in datasheets_by_type}

    # Đưa dữ liệu vào context
    context = {
        'datasheets_by_type': sorted_datasheets_by_type,
        'available_dates': available_dates,
        'selected_date': selected_date,
    }

    return render(request, 'main_app/daily_signal.html', context)