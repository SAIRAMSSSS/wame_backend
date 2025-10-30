from rest_framework import serializers
from .models import Profile, Workout, Exercise, PostureAnalysis
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
        fields = ('id', 'user', 'bio', 'profile_picture')
        
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