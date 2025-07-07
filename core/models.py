# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# Complaint Categories
CATEGORY_CHOICES = [
    ('academics', 'Academics'),
    ('facilities', 'Facilities'),
    ('staff', 'Staff'),
    ('harassment', 'Harassment'),
    ('other', 'Other'),
]

STATUS_CHOICES = [
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('resolved', 'Resolved'),
    ('escalated', 'Escalated'),
]

ROLE_CHOICES = [
    ('student', 'Student'),
    ('staff', 'Staff'), 
    ('admin', 'Admin'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=50)
    department = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    department = models.CharField(max_length=100, blank=True)
    date_of_incident = models.DateField(null=True, blank=True)
    file_attachment = models.FileField(upload_to='complaint_files/', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.author.username} on {self.complaint.title}"

    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To: {self.user.username} | {'Read' if self.is_read else 'Unread'}"

