from rest_framework import serializers
from .models import (
    Profile, Workout, Exercise, PostureAnalysis,
    Tournament, Team, Player, Match, Field, SpiritScore,
    Attendance, TournamentAnnouncement, VisitorRegistration
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
    profile_picture_url = serializers.SerializerMethodField()
    # Add user fields as direct fields for convenience
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = ('id', 'user', 'bio', 'profile_picture', 'profile_picture_url', 'user_type', 'role', 'phone', 'age', 
                 'address', 'school', 'team_name', 'coach_name', 'profile_completed', 'team_role',
                 'google_id', 'google_email', 'first_name', 'last_name', 'email')
        read_only_fields = ('google_id', 'google_email', 'profile_picture_url', 'first_name', 'last_name', 'email')
    
    def get_profile_picture_url(self, obj):
        """Return full URL for profile picture"""
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None
        

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


# =============================================================================
# TOURNAMENT SERIALIZERS
# =============================================================================

# --- Field Serializer ---
class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = '__all__'


# --- Tournament Serializer ---
class TournamentSerializer(serializers.ModelSerializer):
    tournament_director_name = serializers.CharField(source='tournament_director.get_full_name', read_only=True)
    fields = FieldSerializer(many=True, read_only=True)
    team_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = '__all__'
    
    def get_team_count(self, obj):
        return obj.teams.filter(status='approved').count()


# --- Player Serializer ---
class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = Player
        fields = '__all__'


# --- Team Serializer ---
class TeamSerializer(serializers.ModelSerializer):
    captain_name = serializers.CharField(source='captain.get_full_name', read_only=True)
    captain_email = serializers.EmailField(source='captain.email', read_only=True)
    players = PlayerSerializer(many=True, read_only=True)
    player_count = serializers.SerializerMethodField()
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'
    
    def get_player_count(self, obj):
        return obj.players.count()


# --- Spirit Score Serializer ---
class SpiritScoreSerializer(serializers.ModelSerializer):
    scoring_team_name = serializers.CharField(source='scoring_team.name', read_only=True)
    receiving_team_name = serializers.CharField(source='receiving_team.name', read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    
    class Meta:
        model = SpiritScore
        fields = '__all__'
        read_only_fields = ('total_score',)


# --- Match Serializer ---
class MatchSerializer(serializers.ModelSerializer):
    team_a_name = serializers.CharField(source='team_a.name', read_only=True)
    team_b_name = serializers.CharField(source='team_b.name', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    winner = serializers.SerializerMethodField()
    spirit_scores = SpiritScoreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Match
        fields = '__all__'
    
    def get_winner(self, obj):
        winner = obj.get_winner()
        return winner.name if winner else None


# --- Attendance Serializer ---
class AttendanceSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.full_name', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'


# --- Tournament Announcement Serializer ---
class TournamentAnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = TournamentAnnouncement
        fields = '__all__'


# --- Visitor Registration Serializer ---
class VisitorRegistrationSerializer(serializers.ModelSerializer):
    tournament_name = serializers.CharField(source='tournament.name', read_only=True)
    
    class Meta:
        model = VisitorRegistration
        fields = '__all__'