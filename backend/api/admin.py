from django.contrib import admin
from .models import (
    Profile, Workout, Exercise, PostureAnalysis, FitnessLog,
    Tournament, Team, Player, Match, Field, SpiritScore, Attendance,
    TournamentAnnouncement, VisitorRegistration, Schedule
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
    list_display = ['name', 'location', 'start_date', 'end_date', 'status', 'max_teams', 'tournament_director']
    list_filter = ['status', 'tournament_format', 'start_date']
    search_fields = ['name', 'location', 'tournament_director__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ()
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'rules', 'location')
        }),
        ('Tournament Details', {
            'fields': ('tournament_format', 'status', 'max_teams', 'min_players_per_team', 'max_players_per_team')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Branding & Media', {
            'fields': ('banner_image', 'sponsors')
        }),
        ('Administration', {
            'fields': ('tournament_director', 'created_at', 'updated_at')
        }),
    )

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'tournament', 'is_active']
    list_filter = ['tournament', 'is_active']
    search_fields = ['name', 'tournament__name']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'tournament', 'captain', 'status', 'wins', 'losses', 'average_spirit_score']
    list_filter = ['tournament', 'status']
    search_fields = ['name', 'captain__username', 'home_city']
    readonly_fields = ['wins', 'losses', 'draws', 'points_for', 'points_against', 'average_spirit_score', 'registered_at', 'updated_at']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('tournament', 'name', 'home_city', 'team_logo', 'status')
        }),
        ('Management', {
            'fields': ('captain', 'manager')
        }),
        ('Statistics', {
            'fields': ('wins', 'losses', 'draws', 'points_for', 'points_against', 'average_spirit_score'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('registered_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'team', 'jersey_number', 'position', 'age', 'gender', 'is_verified']
    list_filter = ['tournament', 'team', 'gender', 'experience_level', 'is_verified']
    search_fields = ['full_name', 'email', 'team__name']
    readonly_fields = ['registered_at']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['match_number', 'tournament', 'team_a', 'team_b', 'match_date', 'start_time', 'field', 'status']
    list_filter = ['tournament', 'status', 'match_date', 'field']
    search_fields = ['team_a__name', 'team_b__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'match_date'
    
    fieldsets = (
        ('Match Details', {
            'fields': ('tournament', 'match_number', 'round_number', 'field')
        }),
        ('Teams', {
            'fields': ('team_a', 'team_b')
        }),
        ('Schedule', {
            'fields': ('match_date', 'start_time', 'end_time')
        }),
        ('Scores & Status', {
            'fields': ('team_a_score', 'team_b_score', 'status')
        }),
        ('Officials', {
            'fields': ('referee', 'scorer')
        }),
        ('Media', {
            'fields': ('photos',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SpiritScore)
class SpiritScoreAdmin(admin.ModelAdmin):
    list_display = ['match', 'scoring_team', 'receiving_team', 'total_score', 'is_submitted', 'submitted_at']
    list_filter = ['match__tournament', 'is_submitted', 'submitted_at']
    search_fields = ['scoring_team__name', 'receiving_team__name']
    readonly_fields = ['total_score', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Match & Teams', {
            'fields': ('match', 'scoring_team', 'receiving_team')
        }),
        ('Spirit Categories (0-4 scale)', {
            'fields': ('rules_knowledge', 'fouls_and_contact', 'fair_mindedness', 
                      'positive_attitude', 'communication', 'total_score')
        }),
        ('Feedback', {
            'fields': ('comments',)
        }),
        ('Submission', {
            'fields': ('is_submitted', 'submitted_by', 'submitted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['player', 'date', 'is_present', 'match', 'marked_by', 'marked_at']
    list_filter = ['tournament', 'date', 'is_present']
    search_fields = ['player__full_name', 'player__team__name']
    readonly_fields = ['marked_at']

@admin.register(TournamentAnnouncement)
class TournamentAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'title', 'is_urgent', 'created_by', 'created_at']
    list_filter = ['tournament', 'is_urgent', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']

@admin.register(VisitorRegistration)
class VisitorRegistrationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'tournament', 'organization', 'purpose', 'registered_at']
    list_filter = ['tournament', 'purpose', 'registered_at']
    search_fields = ['full_name', 'email', 'organization']
    readonly_fields = ['registered_at']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'start_time', 'end_time', 'location']
    list_filter = ['event_type', 'date']
    search_fields = ['title', 'location']
