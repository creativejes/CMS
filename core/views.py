from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from .forms import ComplaintForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from .models import Complaint
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect
from .models import Complaint, Comment


# Home Page
def home(request):
    return render(request, 'core/home.html')

# Login Page
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Login attempt — Username: {username}, Password: {'*' * len(password)}")

        user = authenticate(request, username=username, password=password)
        if user:
            print(f"Login successful for {user.username} (ID: {user.id})")
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            #  Handle missing profile gracefully
            from core.models import Profile
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user, role='admin' if user.is_superuser else 'student')

            #  Now redirect based on role
            if user.is_superuser or user.profile.role == 'admin':
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            print(" Authentication failed")
            messages.error(request, 'Invalid username or password')
    return render(request, 'core/login.html')



# Register Page
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)  # include avatar upload
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = profile_form.cleaned_data['role']  # Assign role
            profile.department = profile_form.cleaned_data['department']  # Assign department
            profile.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    context = {
        'form': form,
        'profile_form': profile_form
    }
    return render(request, 'core/register.html', context)


#logout view
def custom_logout(request):
    logout(request)
    messages.success(request, "You’ve been logged out.")
    return redirect("login")

# submit complaint view
@login_required
def submit_complaint(request):
    if request.method == 'POST':
        print(" Received POST submission")
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            print(" Complaint saved for", request.user.username)  # DEBUG
            messages.success(request, 'Your complaint has been submitted successfully.')
            return redirect('submit_complaint')  # stay on same page
        else:
            print(" Form is invalid:", form.errors)  #  DEBUG
    else:
        form = ComplaintForm()

    return render(request, 'core/submit_complaint.html', {'form': form})

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    complaints = Complaint.objects.all()

    total_complaints = complaints.count()
    resolved = complaints.filter(status='resolved').count()
    pending = complaints.filter(status='pending').count()
    escalated = complaints.filter(status='escalated').count()

    stats_by_category = complaints.values('category').annotate(total=Count('id'))

    context = {
        "total": total_complaints,
        "resolved": resolved,
        "pending": pending,
        "escalated": escalated,
        "stats_by_category": stats_by_category,
    }
    return render(request, "core/admin_dashboard.html", context)



@login_required
def dashboard(request):
    complaints = Complaint.objects.filter(user=request.user)
    recent_complaints = complaints.order_by('-submitted_at')[:5]  
    stats_by_category = complaints.values('category').annotate(total=Count('id'))
    category_labels = [item['category'] for item in stats_by_category]
    category_counts = [item['total'] for item in stats_by_category]

    context = {
        'recent_complaints': recent_complaints,
        'resolved_count': complaints.filter(status='resolved').count(),
        'pending_count': complaints.filter(status__in=['submitted', 'under_review']).count(),
        'total_count': complaints.count(),
        'category_labels': category_labels,
        'category_counts': category_counts,
    }
    return render(request, 'core/dashboard.html', context)



@login_required
def resolved_complaints(request):
    search_query = request.GET.get('search', '')
    complaint_list = Complaint.objects.filter(user=request.user, status='resolved')

    if search_query:
        complaint_list = complaint_list.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(complaint_list, 6)  # 6 complaints per page
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)

    return render(request, 'core/resolved_complaints.html', {'complaints': complaints})


@login_required
def unresolved_complaints(request):
    search_query = request.GET.get('search', '')
    complaint_list = Complaint.objects.filter(user=request.user).exclude(status='resolved')

    if search_query:
        complaint_list = complaint_list.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(complaint_list, 6)
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)

    return render(request, 'core/unresolved_complaints.html', {'complaints': complaints})


@login_required
def my_complaints(request):
    search_query = request.GET.get('search', '')
    complaint_list = Complaint.objects.filter(user=request.user)

    if search_query:
        complaint_list = complaint_list.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(complaint_list, 6)
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)

    return render(request, 'core/my_complaints.html', {'complaints': complaints})


@login_required
def complaint_stats(request):
    user_complaints = Complaint.objects.filter(user=request.user)

    # Bar chart data: category breakdown
    category_data = user_complaints.values('category').annotate(count=Count('id'))
    category_labels = [item['category'].title() for item in category_data]
    category_values = [item['count'] for item in category_data]

    # Doughnut chart data: status breakdown
    status_data = user_complaints.values('status').annotate(count=Count('id'))
    status_labels = [item['status'].replace('_', ' ').title() for item in status_data]
    status_values = [item['count'] for item in status_data]

    context = {
        'category_data': {
            'labels': category_labels,
            'values': category_values
        },
        'status_data': {
            'labels': status_labels,
            'values': status_values
        }
    }
    return render(request, 'core/complaint_stats.html', context)

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        # Update basic info
        user.email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        if full_name:
            name_parts = full_name.split(' ')
            user.first_name = name_parts[0]
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        user.save()

        # Update profile info
        profile.student_id = request.POST.get('student_id')
        profile.department = request.POST.get('department')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()

        # Handle password change
        print("change password")
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Important to keep session alive
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Passwords do not match.")

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'core/profile.html')

@login_required
def settings_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        request.user.email = request.POST.get('email')
        profile.notif_email = 'notif_email' in request.POST
        profile.notif_sms = 'notif_sms' in request.POST
        profile.notif_inapp = 'notif_inapp' in request.POST
        request.user.save()
        profile.save()

        messages.success(request, "Settings saved.")
        return redirect('settings')

    return render(request, 'core/settings.html')

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    status = request.GET.get('status')
    category = request.GET.get('category')

    complaints = Complaint.objects.all()

    if status and status != 'all':
        complaints = complaints.filter(status=status)

    if category and category != 'all':
        complaints = complaints.filter(category=category)

    # Get unique category list for dropdown
    categories = Complaint.objects.values_list('category', flat=True).distinct()

    # KPI counts
    total_complaints = complaints.count()
    resolved_complaints = complaints.filter(status='resolved').count()
    pending_complaints = complaints.filter(status='pending').count()
    escalated_complaints = complaints.filter(status='escalated').count()

    # Chart data
    status_data = complaints.values('status').annotate(count=Count('id'))
    category_data = complaints.values('category').annotate(count=Count('id'))

    status_labels = [s['status'].capitalize() for s in status_data]
    status_counts = [s['count'] for s in status_data]
    category_labels = [c['category'] for c in category_data]
    category_counts = [c['count'] for c in category_data]

    context = {
        'complaints': complaints.order_by('-submitted_at'),
        'categories': categories,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'escalated_complaints': escalated_complaints,
        'status_labels': status_labels,
        'status_counts': status_counts,
        'category_labels': category_labels,
        'category_counts': category_counts,
    }

    return render(request, 'core/admin_dashboard.html', context)

@login_required
def view_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    # Base template based on role
    base_template = 'core/base_admin.html' if request.user.profile.role == 'admin' else 'core/base.html'

    if request.method == 'POST':
        # Admin: update complaint status
        if 'update_status' in request.POST and request.user.profile.role == 'admin':
            new_status = request.POST.get('status')
            if new_status and new_status != complaint.status:
                complaint.status = new_status
                complaint.save()
                messages.success(request, f" Complaint status updated to {new_status}.")
            else:
                messages.info(request, "No status change was made.")

        # Admin: add reply
        elif 'add_reply' in request.POST and request.user.profile.role == 'admin':
            reply = request.POST.get('reply')
            if reply:
                Comment.objects.create(
                    complaint=complaint,
                    author=request.user,
                    content=reply
                )
                messages.success(request, " Reply added successfully.")

        return redirect('view_complaint', complaint_id=complaint.id)

    return render(request, 'core/view_complaint.html', {
        'complaint': complaint,
        'base_template': base_template
    })
