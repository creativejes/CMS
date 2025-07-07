from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from . import views
from .views import custom_logout
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect



urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("submit/", views.submit_complaint, name="submit_complaint"),
    path("logout/", custom_logout, name="logout"),
    path("complaints/", views.my_complaints, name="complaints"),
    path("complaints/unresolved/", views.unresolved_complaints, name="unresolved_complaints"),
    path("complaints/resolved/", views.resolved_complaints, name="resolved_complaints"),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('complaints/stats/', views.complaint_stats, name='complaint_stats'),
    path('complaints/', views.my_complaints, name='my_complaints'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('complaints/<int:complaint_id>/', views.view_complaint, name='view_complaint'),

    



#password reset link 
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    path('password-change/', auth_views.PasswordChangeView.as_view(
    template_name='registration/password_change_form.html'
    ), name='change_password'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
    template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    
]