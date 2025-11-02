from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Profile,Workout,Exercise,PostureAnalysis
from .serializers import ProfileSerializer,WorkoutSerializer,ExerciseSerializer,PostureAnalysisSerializer
from django.db.models import Count # For stats
from django.contrib.auth import authenticate, login
from django.conf import settings
from twilio.rest import Client
import random
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


# --- Phone Login View ---
class PhoneLoginView(APIView):
    """POST /api/auth/send_otp/ - Send OTP to phone number"""
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        role = request.data.get('role')  # student, coach, volunteer

        if not phone_number or not role:
            return Response({"error": "Phone number and role are required."}, status=status.HTTP_400_BAD_REQUEST)

        if role not in ['student', 'coach', 'volunteer']:
            return Response({"error": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if profile exists with this phone and role
        try:
            profile = Profile.objects.get(phone_number=phone_number, role=role)
            user = profile.user
        except Profile.DoesNotExist:
            return Response({"error": "No user found with this phone number and role."}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP in session or cache (for simplicity, using session)
        request.session['otp'] = otp
        request.session['phone_number'] = phone_number
        request.session['role'] = role

        # Send OTP via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            message = client.messages.create(
                body=f"Your OTP for login is: {otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        except Exception as e:
            return Response({"error": "Failed to send OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """POST /api/auth/verify_otp/ - Verify OTP and login"""
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get('otp')

        if not otp:
            return Response({"error": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check OTP
        if otp != request.session.get('otp'):
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        phone_number = request.session.get('phone_number')
        role = request.session.get('role')

        try:
            profile = Profile.objects.get(phone_number=phone_number, role=role)
            user = profile.user
        except Profile.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Login user
        login(request, user)

        # Clear session
        del request.session['otp']
        del request.session['phone_number']
        del request.session['role']

        return Response({"message": "Login successful.", "user_id": user.id, "role": role}, status=status.HTTP_200_OK)


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
