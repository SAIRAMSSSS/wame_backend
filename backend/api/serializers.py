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