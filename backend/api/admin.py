from django.contrib import admin
from .models import (
    Profile, Workout, Exercise, PostureAnalysis, 
    FitnessLog, Tournament, TournamentRegistration, Schedule
)

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'google_email', 'google_id', 'total_points']
    list_filter = ['user_type']
    search_fields = ['user__username', 'user__email', 'google_email']
    readonly_fields = ['google_id', 'google_access_token', 'google_refresh_token', 'google_token_expiry']

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
