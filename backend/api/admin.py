from django.contrib import admin
from .models import (
    Profile, Workout, Exercise, PostureAnalysis, 
    FitnessLog, Tournament, TournamentRegistration, Schedule
)

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'get_email', 'user_type', 'team_name', 'team_role', 'coach_name', 'profile_completed', 'total_points']
    list_filter = ['user_type', 'profile_completed', 'team_role']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'google_email', 'coach_name', 'team_name']
    readonly_fields = ['google_id', 'google_access_token', 'google_refresh_token', 'google_token_expiry', 'profile_completed']
    
    def get_full_name(self, obj):
        """Display user's full name"""
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_email(self, obj):
        """Display user's email"""
        return obj.user.email or obj.google_email or 'No email'
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type', 'bio', 'profile_picture')
        }),
        ('Contact Details', {
            'fields': ('phone', 'age', 'school', 'address')
        }),
        ('Team Information', {
            'fields': ('coach_name', 'team_name', 'team_role', 'profile_completed')
        }),
        ('Fitness Tracking', {
            'fields': ('total_points',)
        }),
        ('Google OAuth', {
            'fields': ('google_id', 'google_email', 'google_access_token', 'google_refresh_token', 'google_token_expiry'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FitnessLog)
class FitnessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'steps', 'calories_burned', 'active_minutes', 'distance_km']
    list_filter = ['date', 'user']
    search_fields = ['user__username']
    ordering = ['-date']
    date_hierarchy = 'date'

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date', 'is_completed']
    list_filter = ['is_completed', 'date']
    search_fields = ['name', 'user__username']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'workout', 'sets', 'reps', 'duration_minutes', 'is_completed']
    list_filter = ['is_completed']
    search_fields = ['name', 'workout__name']

@admin.register(PostureAnalysis)
class PostureAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'exercise', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username']

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'start_date', 'end_date', 'status', 'max_participants']
    list_filter = ['status', 'start_date']
    search_fields = ['name', 'location']

@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'user', 'team_name', 'registered_at']
    list_filter = ['tournament', 'registered_at']
    search_fields = ['user__username', 'team_name']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'start_time', 'end_time', 'location']
    list_filter = ['event_type', 'date']
    search_fields = ['title', 'location']
