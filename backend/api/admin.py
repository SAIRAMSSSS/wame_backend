from django.contrib import admin
from .models import (
    Profile, Workout, Exercise, PostureAnalysis,
    Tournament, Team, Player, Match, Field, SpiritScore,
    Attendance, TournamentAnnouncement, VisitorRegistration
)

# Register your models here.

# --- Fitness Models ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'role', 'profile_completed', 'phone')
    list_filter = ('user_type', 'role', 'profile_completed')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date', 'is_completed')
    list_filter = ('is_completed', 'date')
    search_fields = ('name', 'user__username')

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'workout', 'sets', 'reps', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('name', 'workout__name')

@admin.register(PostureAnalysis)
class PostureAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)


# --- Tournament Management Models ---
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'start_date', 'end_date', 'status', 'tournament_director')
    list_filter = ('status', 'tournament_format', 'start_date')
    search_fields = ('name', 'location')
    date_hierarchy = 'start_date'

@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'is_active')
    list_filter = ('tournament', 'is_active')
    search_fields = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'captain', 'status', 'wins', 'losses', 'spirit_score_average')
    list_filter = ('tournament', 'status')
    search_fields = ('name', 'captain__username')
    ordering = ('-wins', '-spirit_score_average')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'team', 'tournament', 'gender', 'age', 'jersey_number', 'is_verified')
    list_filter = ('tournament', 'team', 'gender', 'experience_level', 'is_verified')
    search_fields = ('full_name', 'email', 'phone')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_number', 'tournament', 'team_a', 'team_b', 'team_a_score', 'team_b_score', 'status', 'match_date')
    list_filter = ('tournament', 'status', 'match_date')
    search_fields = ('team_a__name', 'team_b__name')
    date_hierarchy = 'match_date'

@admin.register(SpiritScore)
class SpiritScoreAdmin(admin.ModelAdmin):
    list_display = ('match', 'scoring_team', 'receiving_team', 'total_score', 'is_submitted', 'created_at')
    list_filter = ('is_submitted', 'created_at')
    search_fields = ('scoring_team__name', 'receiving_team__name')
    readonly_fields = ('total_score',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('player', 'tournament', 'match', 'date', 'is_present', 'marked_by')
    list_filter = ('tournament', 'is_present', 'date')
    search_fields = ('player__full_name',)
    date_hierarchy = 'date'

@admin.register(TournamentAnnouncement)
class TournamentAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'tournament', 'is_urgent', 'created_by', 'created_at')
    list_filter = ('tournament', 'is_urgent', 'created_at')
    search_fields = ('title', 'message')
    date_hierarchy = 'created_at'

@admin.register(VisitorRegistration)
class VisitorRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'email', 'phone', 'purpose', 'registered_at')
    list_filter = ('tournament', 'purpose', 'registered_at')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'registered_at'
