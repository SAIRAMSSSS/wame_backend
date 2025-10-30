from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Profile,Workout,Exercise,PostureAnalysis
from .serializers import ProfileSerializer,WorkoutSerializer,ExerciseSerializer,PostureAnalysisSerializer
from django.db.models import Count # For stats
import json


class HealthCheckView(APIView):
    """GET /api/health/ - Check if API is running"""
    permission_classes = [AllowAny]
    def get(self,request):
        return Response({"status": "API is running"}, status=status.HTTP_200_OK)
    
    # --- User Profiles ---
class ProfileViewSet(viewsets.ModelViewSet):
    """CRUD for User Profiles"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own profile in most cases, or all if staff.
        # For simplicity, let's allow listing all profiles for now.
        return Profile.objects.all() 
    
    # Custom Endpoint: GET /api/profiles/me/
    @action(detail=False, url_path='me')
    def me(self, request):
        """Get the profile of the currently authenticated user."""
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Automatically set the user for the profile (this should typically be done on User creation)
        serializer.save(user=self.request.user)
    
    # Custom logic to ensure users only modify their own profile
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:
            return Response({"detail": "You do not have permission to edit this profile."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


# --- Workouts ---
class WorkoutViewSet(viewsets.ModelViewSet):
    """CRUD for Workouts and custom actions"""
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only see their own workouts
        return Workout.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user
        serializer.save(user=self.request.user)

    # Custom Endpoint: POST /api/workouts/{id}/complete/
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        workout = self.get_object()
        workout.is_completed = True
        workout.save()
        return Response({'status': 'workout marked as completed'})
    
    # Custom Endpoint: GET /api/workouts/stats/
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get workout statistics for the user."""
        completed_count = self.get_queryset().filter(is_completed=True).count()
        total_count = self.get_queryset().count()
        
        return Response({
            'total_workouts': total_count,
            'completed_workouts': completed_count,
            'completion_rate': f"{completed_count / total_count * 100:.2f}%" if total_count > 0 else "0%"
        })


# --- Exercises ---
class ExerciseViewSet(viewsets.ModelViewSet):
    """CRUD for Exercises and custom actions"""
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only see exercises related to their workouts
        return Exercise.objects.filter(workout__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the workout belongs to the user
        workout_id = self.request.data.get('workout') # Expect workout ID in the request data
        try:
            workout = Workout.objects.get(pk=workout_id, user=self.request.user)
            serializer.save(workout=workout)
        except Workout.DoesNotExist:
            raise serializers.ValidationError("Workout not found or does not belong to the user.")

    # Custom Endpoint: POST /api/exercises/{id}/complete/
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        exercise = self.get_object()
        exercise.is_completed = True
        exercise.save()
        return Response({'status': 'exercise marked as completed'})


# --- Posture Analysis ---
class PostureAnalysisViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """List all analyses"""
    queryset = PostureAnalysis.objects.all()
    serializer_class = PostureAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only see their own analyses
        return PostureAnalysis.objects.filter(user=self.request.user)


class AnalyzeImageView(APIView):
    """POST /api/posture/analyze_image/ - Analyze single image"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        image_file = request.FILES.get('image')
        workout_id = request.data.get('workout_id')
        exercise_id = request.data.get('exercise_id')

        # 1. Validation and File Handling (You must implement this)
        if not image_file:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. MediaPipe/AI Analysis (Placeholder Logic)
        # In a real app, this is where you'd run the MediaPipe model on the image.
        analysis_result = {
            "keypoints_detected": 15,
            "score": 0.95,
            "feedback": "Excellent posture. Keep your back straight."
        }
        
        # 3. Save Analysis Result
        PostureAnalysis.objects.create(
            user=request.user,
            workout_id=workout_id,
            exercise_id=exercise_id,
            media_url="<placeholder_url_to_uploaded_image>", # Replace with the actual URL from Supabase after upload
            analysis_data=analysis_result
        )

        return Response({"status": "Analysis successful", "result": analysis_result}, status=status.HTTP_201_CREATED)


# --- Recommendation Engine ---
class RecommendationView(APIView):
    """GET /api/recommendations/ - List recommendations & POST /api/recommendations/generate/ - Generate"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Placeholder: Retrieve last 5 generated recommendations
        recommendations = ["Try HIIT for cardio.", "Focus on core strength.", "Increase weight for squats."]
        return Response({"recommendations": recommendations}, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        # Placeholder: Logic to generate AI recommendations based on user history
        # You'd query user's workouts, stats, and run your AI/ML logic here.
        new_recommendation = "Based on your 5 completed workouts, we recommend a 3-day strength training split."
        return Response({"status": "Generation successful", "new_recommendation": new_recommendation}, status=status.HTTP_201_CREATED)