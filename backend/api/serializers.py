from rest_framework import serializers
from .models import (
    Profile, Workout, Exercise, PostureAnalysis,
    Tournament, Team, Player, Match, Field, SpiritScore, Attendance, 
    TournamentAnnouncement, VisitorRegistration
)
from django.contrib.auth.models import User

# --- Base User Serializer (for nested relationships) ---
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


# --- Profile Serializer ---
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # Allow updating user's first_name, last_name, email through profile
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', required=False, allow_blank=True)
    # Return full URL for profile picture
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'first_name', 'last_name', 'email', 
            'user_type', 'bio', 'phone', 'age', 'school', 'address',
            'coach_name', 'team_name', 'team_role', 'profile_completed',
            'total_points', 'google_id', 'google_email', 'profile_picture', 'profile_picture_url'
        )
        read_only_fields = ('user', 'user_type', 'total_points', 'google_id', 'google_email', 'profile_picture_url')
    
    def get_profile_picture_url(self, obj):
        """Return full URL for profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None
        
    def update(self, instance, validated_data):
        # Handle nested user update
        user_data = {}
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
        
        # Update user fields
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Check if profile is completed
        if all([
            instance.user.first_name,
            instance.user.email,
            instance.coach_name,
            instance.team_name,
            instance.team_role
        ]):
            instance.profile_completed = True
        else:
            instance.profile_completed = False
            
        instance.save()
        return instance
        
    def create(self, validated_data):
        # We handle User creation separately, so this serializer focuses on Profile updates
        raise serializers.ValidationError("Use the default User endpoint for user creation.")
        

# --- Exercise Serializer ---
class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        # 'workout' is read-only when listing/creating exercises within a workout
        fields = ('id', 'name', 'description', 'sets', 'reps', 'duration_minutes', 'is_completed')


# --- Workout Serializer ---
class WorkoutSerializer(serializers.ModelSerializer):
    exercises = ExerciseSerializer(many=True, read_only=True) # Nested exercises
    user = UserSerializer(read_only=True) # Display user info

    class Meta:
        model = Workout
        fields = ('id', 'user', 'name', 'description', 'date', 'is_completed', 'exercises')


# --- Posture Analysis Serializer ---
class PostureAnalysisSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostureAnalysis
        fields = '__all__'
        read_only_fields = ('user',) # User is set by the view


# ===============================
# TOURNAMENT MANAGEMENT SERIALIZERS
# ===============================

# --- Field Serializer ---
class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ('id', 'name', 'location_details', 'is_active')


# --- Player Serializer ---
class PlayerSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = (
            'id', 'user', 'user_details', 'team', 'team_name', 'tournament',
            'full_name', 'email', 'phone', 'gender', 'age',
            'jersey_number', 'position', 'experience_level',
            'is_verified', 'registered_at'
        )
        read_only_fields = ('registered_at',)


# --- Team Serializer ---
class TeamSerializer(serializers.ModelSerializer):
    captain_details = UserSerializer(source='captain', read_only=True)
    manager_details = UserSerializer(source='manager', read_only=True)
    players = PlayerSerializer(many=True, read_only=True)
    player_count = serializers.SerializerMethodField()
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    team_logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = (
            'id', 'tournament', 'tournament_name', 'name', 'captain', 'captain_details',
            'manager', 'manager_details', 'status', 'home_city', 'team_logo', 'team_logo_url',
            'wins', 'losses', 'draws', 'points_for', 'points_against',
            'average_spirit_score', 'players', 'player_count',
            'registered_at', 'updated_at'
        )
        read_only_fields = ('wins', 'losses', 'draws', 'points_for', 'points_against', 
                           'average_spirit_score', 'registered_at', 'updated_at')
    
    def get_player_count(self, obj):
        return obj.players.count()
    
    def get_team_logo_url(self, obj):
        if obj.team_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.team_logo.url)
            return obj.team_logo.url
        return None


# --- Spirit Score Serializer ---
class SpiritScoreSerializer(serializers.ModelSerializer):
    scoring_team_name = serializers.CharField(source='scoring_team.name', read_only=True)
    receiving_team_name = serializers.CharField(source='receiving_team.name', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.username', read_only=True)
    total_score = serializers.ReadOnlyField()
    match_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SpiritScore
        fields = (
            'id', 'match', 'match_details', 'scoring_team', 'scoring_team_name',
            'receiving_team', 'receiving_team_name', 'rules_knowledge',
            'fouls_and_contact', 'fair_mindedness', 'positive_attitude',
            'communication', 'total_score', 'comments', 'is_submitted',
            'submitted_by', 'submitted_by_name', 'submitted_at',
            'created_at', 'updated_at'
        )
        read_only_fields = ('total_score', 'submitted_at', 'created_at', 'updated_at')
    
    def get_match_details(self, obj):
        return {
            'team_a': obj.match.team_a.name,
            'team_b': obj.match.team_b.name,
            'date': obj.match.match_date,
        }


# --- Match Serializer ---
class MatchSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    team_a_details = TeamSerializer(source='team_a', read_only=True)
    team_b_details = TeamSerializer(source='team_b', read_only=True)
    winner = serializers.SerializerMethodField()
    spirit_scores = SpiritScoreSerializer(many=True, read_only=True)
    referee_name = serializers.CharField(source='referee.username', read_only=True)
    scorer_name = serializers.CharField(source='scorer.username', read_only=True)
    
    class Meta:
        model = Match
        fields = (
            'id', 'tournament', 'tournament_name', 'field', 'field_name',
            'team_a', 'team_a_details', 'team_b', 'team_b_details',
            'match_date', 'start_time', 'end_time', 'round_number', 'match_number',
            'team_a_score', 'team_b_score', 'status', 'winner',
            'referee', 'referee_name', 'scorer', 'scorer_name',
            'spirit_scores', 'photos', 'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_winner(self, obj):
        winner = obj.get_winner()
        if winner:
            return {
                'id': winner.id,
                'name': winner.name
            }
        return None


# --- Tournament Serializer ---
class TournamentSerializer(serializers.ModelSerializer):
    director_details = UserSerializer(source='tournament_director', read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    teams = TeamSerializer(many=True, read_only=True)
    matches = MatchSerializer(many=True, read_only=True)
    banner_image_url = serializers.SerializerMethodField()
    registered_teams_count = serializers.SerializerMethodField()
    total_players_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = (
            'id', 'name', 'description', 'rules', 'location',
            'start_date', 'end_date', 'registration_deadline',
            'status', 'tournament_format', 'max_teams',
            'min_players_per_team', 'max_players_per_team',
            'banner_image', 'banner_image_url', 'sponsors',
            'tournament_director', 'director_details',
            'registered_teams_count', 'total_players_count',
            'fields', 'teams', 'matches',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
    
    def get_banner_image_url(self, obj):
        if obj.banner_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
            return obj.banner_image.url
        return None
    
    def get_registered_teams_count(self, obj):
        return obj.get_registered_teams_count()
    
    def get_total_players_count(self, obj):
        return obj.get_total_players_count()


# --- Simplified Tournament List Serializer (for performance) ---
class TournamentListSerializer(serializers.ModelSerializer):
    director_name = serializers.CharField(source='tournament_director.username', read_only=True)
    registered_teams_count = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = (
            'id', 'name', 'description', 'location', 'start_date', 'end_date',
            'status', 'tournament_format', 'max_teams', 'registered_teams_count',
            'banner_image_url', 'director_name', 'created_at'
        )
    
    def get_registered_teams_count(self, obj):
        return obj.get_registered_teams_count()
    
    def get_banner_image_url(self, obj):
        if obj.banner_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.banner_image.url)
            return obj.banner_image.url
        return None


# --- Attendance Serializer ---
class AttendanceSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    match_details = serializers.SerializerMethodField()
    marked_by_name = serializers.CharField(source='marked_by.username', read_only=True)
    
    class Meta:
        model = Attendance
        fields = (
            'id', 'player', 'player_name', 'match', 'match_details',
            'tournament', 'date', 'is_present', 'marked_by',
            'marked_by_name', 'marked_at', 'notes'
        )
        read_only_fields = ('marked_at',)
    
    def get_match_details(self, obj):
        if obj.match:
            return {
                'id': obj.match.id,
                'teams': f"{obj.match.team_a.name} vs {obj.match.team_b.name}",
                'date': obj.match.match_date
            }
        return None


# --- Tournament Announcement Serializer ---
class TournamentAnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = TournamentAnnouncement
        fields = (
            'id', 'tournament', 'tournament_name', 'title', 'message',
            'is_urgent', 'created_by', 'created_by_name', 'created_at'
        )
        read_only_fields = ('created_at',)


# --- Visitor Registration Serializer ---
class VisitorRegistrationSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = VisitorRegistration
        fields = (
            'id', 'tournament', 'tournament_name', 'full_name',
            'email', 'phone', 'organization', 'purpose', 'registered_at'
        )
        read_only_fields = ('registered_at',)