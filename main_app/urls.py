from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chart/', views.chart, name='chart'),
    path('daily-management/', views.daily_management, name='daily_management'),  # Định nghĩa URL này
    path('delete-selected-data/', views.delete_selected_data, name='delete_selected_data'),
    path('delete-all-data/', views.delete_all_data, name='delete_all_data'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admin-panel/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user-info/', views.user_info, name='user_info'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('daily-signal/', views.signal_view, name='daily_signal'),
]
