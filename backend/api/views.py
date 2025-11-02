from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from .models import Profile, Workout, Exercise, PostureAnalysis, FitnessLog, Tournament, TournamentRegistration, Schedule
from .serializers import ProfileSerializer,WorkoutSerializer,ExerciseSerializer,PostureAnalysisSerializer
from django.db.models import Count # For stats
from datetime import date, timedelta, datetime
import json
import os
import random

# Google OAuth imports
try:
    from google.oauth2.credentials import Credentials
except ImportError:
    # Fallback stub so editors/linters don't show unresolved import when
    # google-auth is not installed in the environment.
    # Install the real package for production: pip install google-auth google-auth-oauthlib google-api-python-client
    class Credentials:
        def __init__(self, token=None, refresh_token=None, token_uri=None,
                     client_id=None, client_secret=None, scopes=None, **kwargs):
            self.token = token
            self.refresh_token = refresh_token
            self.token_uri = token_uri
            self.client_id = client_id
            self.client_secret = client_secret
            self.scopes = scopes or []
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class HealthCheckView(APIView):
    """GET /api/health/ - Check if API is running"""
    permission_classes = [AllowAny]
    def get(self,request):
        return Response({"status": "API is running"}, status=status.HTTP_200_OK)


# --- AUTHENTICATION VIEWS ---
class RegisterView(APIView):
    """POST /api/auth/register/ - Register new user"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return Response({"message": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=data['email']).exists():
            return Response({"message": "User with this email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        user = User.objects.create_user(
            username=data['email'],

            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Update profile with additional information
        profile = user.profile
        profile.user_type = data.get('user_type', 'student')
        profile.phone = data.get('phone', '')
        profile.age = data.get('age')
        profile.school = data.get('school', '')
        profile.address = data.get('address', '')
        profile.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "message": "User registered successfully",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": profile.user_type
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/auth/login/ - Login user"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({"message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is None:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "message": "Login successful",
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.profile.user_type
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """POST /api/auth/logout/ - Logout user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


# --- GOOGLE OAUTH VIEWS ---
class GoogleLoginView(APIView):
    """GET /api/auth/google/ - Initiate Google OAuth flow"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Google OAuth configuration from environment variables
        client_id = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET')
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/auth/google/callback/')
        
        # For development, we'll create the OAuth URL manually
        # In production, use google_auth_oauthlib.flow.Flow
        
        scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/fitness.activity.read',
            'https://www.googleapis.com/auth/fitness.body.read',
            'https://www.googleapis.com/auth/fitness.location.read'
        ]
        
        # Build authorization URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope={' '.join(scopes)}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return Response({'auth_url': auth_url}, status=status.HTTP_200_OK)


class GoogleCallbackView(APIView):
    """GET /api/auth/google/callback/ - Handle Google OAuth callback"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        code = request.GET.get('code')
        error = request.GET.get('error')
        
        if error:
            return redirect(f'http://localhost:3000/student/login?error={error}')
        
        if not code:
            return redirect('http://localhost:3000/student/login?error=no_code')
        
        try:
            # Exchange authorization code for tokens
            import requests
            
            token_url = 'https://oauth2.googleapis.com/token'
            data = {
                'code': code,
                'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
                'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/auth/google/callback/'),
                'grant_type': 'authorization_code'
            }
            
            token_response = requests.post(token_url, data=data)
            
            if token_response.status_code != 200:
                print(f"Token exchange failed: {token_response.text}")
                return redirect(f'http://localhost:3000/student/login?error=token_exchange_failed')
            
            token_data = token_response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            
            # Get user info from Google
            userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
            headers = {'Authorization': f'Bearer {access_token}'}
            userinfo_response = requests.get(userinfo_url, headers=headers)
            
            if userinfo_response.status_code != 200:
                print(f"Userinfo failed: {userinfo_response.text}")
                return redirect(f'http://localhost:3000/student/login?error=userinfo_failed')
            
            user_info = userinfo_response.json()
            
            google_id = user_info.get('id')
            email = user_info.get('email')
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            picture_url = user_info.get('picture', '')  # Google profile picture
            
            # Check if user exists with this Google ID
            try:
                profile = Profile.objects.get(google_id=google_id)
                user = profile.user
                created = False
                print(f"Existing user logged in: {email}")
            except Profile.DoesNotExist:
                # Check if user exists with this email
                try:
                    user = User.objects.get(email=email)
                    profile = user.profile
                    created = False
                    print(f"Existing user (by email) logged in: {email}")
                except User.DoesNotExist:
                    # Create new user
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    profile = user.profile
                    profile.user_type = 'student'
                    created = True
                    print(f"New user created: {email} (ID: {user.id})")
            
            # Update profile with Google OAuth data
            from django.utils import timezone
            profile.google_id = google_id
            profile.google_email = email
            profile.google_access_token = access_token
            profile.google_refresh_token = refresh_token
            profile.google_token_expiry = timezone.now() + timedelta(seconds=expires_in)
            
            # Store user's full name if not already set
            if not user.first_name and first_name:
                user.first_name = first_name
            if not user.last_name and last_name:
                user.last_name = last_name
            user.save()
            
            profile.save()
            
            # Log the stored data for verification
            print(f"✅ User data stored in database:")
            print(f"  - User ID: {user.id}")
            print(f"  - Username: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Name: {user.first_name} {user.last_name}")
            print(f"  - Profile ID: {profile.id}")
            print(f"  - Google ID: {profile.google_id}")
            print(f"  - User Type: {profile.user_type}")
            print(f"  - Account Created: {'Yes (new)' if created else 'No (existing)'}")
            
            # Create auth token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Fetch Google Fit data automatically
            try:
                self.sync_google_fit_data(user, access_token)
            except Exception as e:
                print(f"Google Fit sync error: {e}")
            
            # Redirect to dashboard with token
            redirect_url = f'http://localhost:3000/student/home?token={token.key}&google_connected=true&first_time={created}'
            return redirect(redirect_url)
            
        except Exception as e:
            print(f"Google OAuth error: {e}")
            return redirect(f'http://localhost:3000/student/login?error=oauth_failed')
    
    def sync_google_fit_data(self, user, access_token):
        """Fetch and save Google Fit data for the user"""
        try:
            # Build Fitness API service
            credentials = Credentials(token=access_token)
            fitness_service = build('fitness', 'v1', credentials=credentials)
            
            from datetime import datetime as dt
            today = date.today()
            today_dt = dt.combine(today, dt.min.time())
            start_dt = today_dt - timedelta(days=7)
            start_time = int(start_dt.timestamp() * 1000000000)
            end_time = int(today_dt.timestamp() * 1000000000)
            
            # Fetch steps data
            try:
                steps_dataset = fitness_service.users().dataset().aggregate(
                    userId='me',
                    body={
                        'aggregateBy': [{
                            'dataTypeName': 'com.google.step_count.delta',
                            'dataSourceId': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps'
                        }],
                        'bucketByTime': {'durationMillis': 86400000},  # 1 day
                        'startTimeMillis': start_time // 1000000,
                        'endTimeMillis': end_time // 1000000
                    }
                ).execute()
                
                # Parse and save fitness data
                for bucket in steps_dataset.get('bucket', []):
                    timestamp = int(bucket['startTimeMillis']) // 1000
                    log_date = date.fromtimestamp(timestamp)

                    steps = 0
                    for dataset in bucket.get('dataset', []):
                        for point in dataset.get('point', []):
                            steps += point['value'][0]['intVal']

                    # Create or update fitness log
                    FitnessLog.objects.update_or_create(
                        user=user,
                        date=log_date,
                        defaults={
                            'steps': steps,
                            'calories_burned': int(steps * 0.04),  # Rough estimate
                            'active_minutes': int(steps / 100),  # Rough estimate
                            'distance_km': round(steps * 0.0008, 2)  # Rough estimate
                        }
                    )
            except HttpError as e:
                print(f"Google Fit API error: {e}")
                # If Google Fit fails, generate mock data
                self.generate_mock_data(user)
                return  # Exit after generating mock data
        except Exception as e:
            print(f"Google Fit sync error: {e}")
            # Fallback to mock data only if not already handled
            self.generate_mock_data(user)
    
    def generate_mock_data(self, user):
        """Generate mock fitness data if Google Fit is not available"""
        from django.db import IntegrityError
        print(f"📊 Generating mock fitness data for {user.username}...")
        today = date.today()
        fitness_logs_created = 0
        
        for i in range(7):
            log_date = today - timedelta(days=i)
            try:
                fitness_log, created = FitnessLog.objects.update_or_create(
                    user=user,
                    date=log_date,
                    defaults={
                        'calories_burned': random.randint(300, 600),
                        'steps': random.randint(5000, 10000),
                        'active_minutes': random.randint(30, 90),
                        'distance_km': round(random.uniform(3.0, 8.0), 2)
                    }
                )
                if created:
                    fitness_logs_created += 1
            except IntegrityError:
                # If there's a race condition, just skip this entry
                print(f"Skipping duplicate entry for {user.username} on {log_date}")
                continue
        
        print(f"✅ Fitness data stored: {fitness_logs_created} new logs created for {user.username}")
        total_logs = FitnessLog.objects.filter(user=user).count()
        print(f"📈 Total fitness logs in database for {user.username}: {total_logs}")


# --- DATABASE STATS VIEW ---
class DatabaseStatsView(APIView):
    """View to check what data is stored in the database"""
    permission_classes = [AllowAny]  # Remove this in production
    
    def get(self, request):
        try:
            # Count all records
            total_users = User.objects.count()
            total_profiles = Profile.objects.count()
            total_fitness_logs = FitnessLog.objects.count()
            google_oauth_users = Profile.objects.filter(google_id__isnull=False).count()
            
            # Get recent users
            recent_users = []
            for user in User.objects.all().order_by('-id')[:10]:
                profile = user.profile
                fitness_count = FitnessLog.objects.filter(user=user).count()
                recent_users.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'user_type': profile.user_type,
                    'google_id': profile.google_id,
                    'is_google_oauth': bool(profile.google_id),
                    'fitness_logs_count': fitness_count,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            # Get fitness data summary
            fitness_summary = []
            for user in User.objects.all()[:10]:
                logs = FitnessLog.objects.filter(user=user).order_by('-date')[:7]
                if logs:
                    fitness_summary.append({
                        'username': user.username,
                        'total_logs': logs.count(),
                        'latest_log': {
                            'date': logs[0].date.strftime('%Y-%m-%d'),
                            'steps': logs[0].steps,
                            'calories': logs[0].calories_burned,
                            'active_minutes': logs[0].active_minutes
                        }
                    })
            
            return Response({
                'status': 'success',
                'message': 'Database connection active',
                'statistics': {
                    'total_users': total_users,
                    'total_profiles': total_profiles,
                    'google_oauth_users': google_oauth_users,
                    'manual_registration_users': total_users - google_oauth_users,
                    'total_fitness_logs': total_fitness_logs
                },
                'recent_users': recent_users,
                'fitness_data_summary': fitness_summary
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
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
    
    # Custom Endpoint: PUT/PATCH /api/profiles/update-profile/
    @action(detail=False, methods=['put', 'patch'], url_path='update-profile')
    def update_profile(self, request):
        """Update the profile of the currently authenticated user."""
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "profile": serializer.data,
                "profile_completed": serializer.data.get('profile_completed', False)
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Custom Endpoint: GET /api/profiles/check-completion/
    @action(detail=False, methods=['get'], url_path='check-completion')
    def check_completion(self, request):
        """Check if the user's profile is complete."""
        profile = get_object_or_404(Profile, user=request.user)
        
        missing_fields = []
        if not request.user.first_name:
            missing_fields.append('first_name')
        if not request.user.email:
            missing_fields.append('email')
        if not profile.coach_name:
            missing_fields.append('coach_name')
        if not profile.team_name:
            missing_fields.append('team_name')
        if not profile.team_role:
            missing_fields.append('team_role')
        
        return Response({
            "profile_completed": profile.profile_completed,
            "missing_fields": missing_fields,
            "message": "Please complete your profile to access all features." if missing_fields else "Profile is complete!"
        }, status=status.HTTP_200_OK)
    
    # Custom Endpoint: POST /api/profiles/upload-picture/
    @action(detail=False, methods=['post'], url_path='upload-picture')
    def upload_picture(self, request):
        """Upload profile picture for the current user."""
        profile = get_object_or_404(Profile, user=request.user)
        
        if 'profile_picture' not in request.FILES:
            return Response({
                "error": "No profile picture provided"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delete old profile picture if exists
        if profile.profile_picture:
            profile.profile_picture.delete(save=False)
        
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        
        serializer = self.get_serializer(profile, context={'request': request})
        return Response({
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": serializer.data.get('profile_picture_url')
        }, status=status.HTTP_200_OK)

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


# --- STUDENT DASHBOARD VIEWS ---
class StudentFitnessView(APIView):
    """GET /api/student/fitness/ - Get student fitness data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get last 7 days of fitness data
        today = date.today()
        last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        
        fitness_logs = FitnessLog.objects.filter(
            user=request.user,
            date__in=last_7_days
        ).order_by('date')
        
        # Format data for chart
        data = {
            'dates': [log.date.strftime('%a') for log in fitness_logs],
            'calories': [log.calories_burned for log in fitness_logs],
            'steps': [log.steps for log in fitness_logs],
            'active_minutes': [log.active_minutes for log in fitness_logs],
            'today': {
                'calories': fitness_logs.last().calories_burned if fitness_logs.exists() else 0,
                'steps': fitness_logs.last().steps if fitness_logs.exists() else 0,
                'active_minutes': fitness_logs.last().active_minutes if fitness_logs.exists() else 0
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)


class GoogleFitSyncView(APIView):
    """POST /api/student/fitness/sync-google-fit/ - Sync Google Fit data"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Sync fitness data from Google Fit API
        
        To use this endpoint:
        1. Get Google OAuth credentials from Google Cloud Console
        2. Install google-auth and google-api-python-client: pip install google-auth google-api-python-client
        3. Store user's Google access token in Profile model
        4. This endpoint will fetch last 7 days of data from Google Fit
        """
        
        # MOCK DATA for now - Replace with actual Google Fit API call
        today = date.today()
        
        # Simulate fetching data from Google Fit for last 7 days
        import random
        for i in range(7):
            log_date = today - timedelta(days=i)
            
            # Create or update fitness log with Google Fit data
            fitness_log, created = FitnessLog.objects.update_or_create(
                user=request.user,
                date=log_date,
                defaults={
                    'calories_burned': random.randint(300, 600),
                    'steps': random.randint(5000, 10000),
                    'active_minutes': random.randint(30, 90),
                    'distance_km': round(random.uniform(3.0, 8.0), 2)
                }
            )
        
        # Return updated fitness data
        last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        fitness_logs = FitnessLog.objects.filter(
            user=request.user,
            date__in=last_7_days
        ).order_by('date')
        
        data = {
            'dates': [log.date.strftime('%a') for log in fitness_logs],
            'calories': [log.calories_burned for log in fitness_logs],
            'steps': [log.steps for log in fitness_logs],
            'active_minutes': [log.active_minutes for log in fitness_logs],
            'today': {
                'calories': fitness_logs.last().calories_burned if fitness_logs.exists() else 0,
                'steps': fitness_logs.last().steps if fitness_logs.exists() else 0,
                'active_minutes': fitness_logs.last().active_minutes if fitness_logs.exists() else 0
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)


class TournamentListView(APIView):
    """GET /api/tournaments/ - List all tournaments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tournaments = Tournament.objects.filter(status='upcoming').order_by('start_date')
        
        data = []
        for tournament in tournaments:
            is_registered = TournamentRegistration.objects.filter(
                tournament=tournament,
                user=request.user
            ).exists()
            
            data.append({
                'id': tournament.id,
                'name': tournament.name,
                'description': tournament.description,
                'location': tournament.location,
                'start_date': tournament.start_date,
                'end_date': tournament.end_date,
                'status': tournament.status,
                'registration_deadline': tournament.registration_deadline,
                'is_registered': is_registered
            })
        
        return Response(data, status=status.HTTP_200_OK)


class TournamentRegisterView(APIView):
    """POST /api/tournaments/<id>/register/ - Register for tournament"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            return Response({"message": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already registered
        if TournamentRegistration.objects.filter(tournament=tournament, user=request.user).exists():
            return Response({"message": "Already registered for this tournament"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Register
        TournamentRegistration.objects.create(
            tournament=tournament,
            user=request.user,
            team_name=request.data.get('team_name', '')
        )
        
        return Response({"message": "Successfully registered for tournament"}, status=status.HTTP_201_CREATED)


class StudentScheduleView(APIView):
    """GET /api/student/schedule/ - Get student schedule"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get upcoming schedules where user is a participant
        schedules = Schedule.objects.filter(
            participants=request.user,
            date__gte=date.today()
        ).order_by('date', 'start_time')[:10]
        
        data = [{
            'id': schedule.id,
            'title': schedule.title,
            'description': schedule.description,
            'event_type': schedule.event_type,
            'location': schedule.location,
            'date': schedule.date,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time
        } for schedule in schedules]
        
        return Response(data, status=status.HTTP_200_OK)


class LeaderboardView(APIView):
    """GET /api/leaderboard/ - Get leaderboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get top 10 students by total points
        top_students = Profile.objects.filter(
            user_type='student'
        ).order_by('-total_points')[:20]
        
        data = [{
            'rank': idx + 1,
            'name': f"{profile.user.first_name} {profile.user.last_name}",
            'points': profile.total_points,
            'is_current_user': profile.user == request.user
        } for idx, profile in enumerate(top_students)]
        
        return Response(data, status=status.HTTP_200_OK)


class AllStudentsFitnessView(APIView):
    """GET /api/admin/students-fitness/ - Get fitness data for all students (Admin/Coach only)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Check if user is admin or coach
        if request.user.profile.user_type not in ['admin', 'coach']:
            return Response({"message": "Unauthorized. Admin or Coach access required."}, status=status.HTTP_403_FORBIDDEN)
        
        # Get all students with their latest fitness data
        students = User.objects.filter(profile__user_type='student').select_related('profile')
        
        data = []
        today = date.today()
        
        for student in students:
            # Get today's fitness log
            try:
                fitness_log = FitnessLog.objects.get(user=student, date=today)
                today_data = {
                    'calories': fitness_log.calories_burned,
                    'steps': fitness_log.steps,
                    'active_minutes': fitness_log.active_minutes,
                    'distance': fitness_log.distance_km
                }
            except FitnessLog.DoesNotExist:
                today_data = {
                    'calories': 0,
                    'steps': 0,
                    'active_minutes': 0,
                    'distance': 0
                }
            
            # Get last 7 days of data
            last_7_days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
            fitness_logs = FitnessLog.objects.filter(
                user=student,
                date__in=last_7_days
            ).order_by('date')
            
            weekly_data = {
                'dates': [log.date.strftime('%a') for log in fitness_logs],
                'calories': [log.calories_burned for log in fitness_logs],
                'steps': [log.steps for log in fitness_logs]
            }
            
            data.append({
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email,
                'school': student.profile.school or 'N/A',
                'total_points': student.profile.total_points,
                'today': today_data,
                'weekly': weekly_data
            })
        
        return Response(data, status=status.HTTP_200_OK)