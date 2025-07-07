from django.contrib import admin
from .models import Profile, Complaint, Comment

# Inline for comments under each complaint
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    readonly_fields = ('author', 'created_at')
    can_delete = False

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'user', 'submitted_at')
    list_filter = ('category', 'status', 'submitted_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'submitted_at'
    ordering = ('-submitted_at',)
    inlines = [CommentInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'student_id', 'created_at')
    search_fields = ('user__username', 'full_name', 'student_id')
    list_filter = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'author', 'created_at')
    search_fields = ('complaint__title', 'author__username')
    ordering = ('-created_at',)
