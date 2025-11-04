from rest_framework import serializers
from .models import (
    Profile, Workout, Exercise, PostureAnalysis, FitnessLog,
    Tournament, TournamentRegistration, Schedule,
    Team, TeamPlayer, Field, Match, SpiritScore, TournamentBracket, Notification,
    ChildProfile, Session, Attendance, LifeSkillsAssessment, HomeVisit
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

    class Meta:
        model = Profile
        fields = ('id', 'user', 'user_type', 'bio', 'phone', 'age', 'school', 'address', 'total_points', 'profile_picture')

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


# --- Fitness Log Serializer ---
class FitnessLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = FitnessLog
        fields = '__all__'


# --- Tournament Management Serializers ---
class TournamentSerializer(serializers.ModelSerializer):
    director = UserSerializer(read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'


class TournamentRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    tournament = TournamentSerializer(read_only=True)

    class Meta:
        model = TournamentRegistration
        fields = '__all__'


class TeamSerializer(serializers.ModelSerializer):
    captain = UserSerializer(read_only=True)
    manager = UserSerializer(read_only=True)
    tournament = TournamentSerializer(read_only=True)

    class Meta:
        model = Team
        fields = '__all__'


class TeamPlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = TeamPlayer
        fields = '__all__'


class FieldSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer(read_only=True)

    class Meta:
        model = Field
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer(read_only=True)
    field = FieldSerializer(read_only=True)
    team_a = TeamSerializer(read_only=True)
    team_b = TeamSerializer(read_only=True)
    winner = TeamSerializer(read_only=True)

    class Meta:
        model = Match
        fields = '__all__'


class SpiritScoreSerializer(serializers.ModelSerializer):
    match = MatchSerializer(read_only=True)
    submitting_team = TeamSerializer(read_only=True)
    submitted_by = UserSerializer(read_only=True)

    class Meta:
        model = SpiritScore
        fields = '__all__'


class TournamentBracketSerializer(serializers.ModelSerializer):
    tournament = TournamentSerializer(read_only=True)

    class Meta:
        model = TournamentBracket
        fields = '__all__'


# --- Child Development Serializers ---
class ChildProfileSerializer(serializers.ModelSerializer):
    programme_manager = UserSerializer(read_only=True)

    class Meta:
        model = ChildProfile
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    programme_manager = UserSerializer(read_only=True)
    coach = UserSerializer(read_only=True)

    class Meta:
        model = Session
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    session = SessionSerializer(read_only=True)
    child = ChildProfileSerializer(read_only=True)
    marked_by = UserSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'


class LifeSkillsAssessmentSerializer(serializers.ModelSerializer):
    child = ChildProfileSerializer(read_only=True)
    conductor_by = UserSerializer(read_only=True)

    class Meta:
        model = LifeSkillsAssessment
        fields = '__all__'


class HomeVisitSerializer(serializers.ModelSerializer):
    child = ChildProfileSerializer(read_only=True)
    coach = UserSerializer(read_only=True)

    class Meta:
        model = HomeVisit
        fields = '__all__'


# --- Notification Serializer ---
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


# --- Schedule Serializer ---
class ScheduleSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'
