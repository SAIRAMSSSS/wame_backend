from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
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
    
    # Custom Endpoint: GET /api/profiles/check-completion/
    @action(detail=False, methods=['get'], url_path='check-completion')
    def check_completion(self, request):
        """Check if user profile is completed"""
        profile = get_object_or_404(Profile, user=request.user)
        return Response({
            'profile_completed': profile.profile_completed,
            'user_type': profile.user_type,
            'role': profile.role
        })
    
    # Custom Endpoint: PATCH /api/profiles/update-profile/
    @action(detail=False, methods=['patch'], url_path='update-profile')
    def update_profile(self, request):
        """Update the current user's profile"""
        profile = get_object_or_404(Profile, user=request.user)
        
        # Update profile fields
        for field, value in request.data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        # Update user fields (first_name, last_name, email)
        user = request.user
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        
        user.save()
        
        # Check if profile is complete (all required fields filled)
        required_fields_filled = all([
            user.first_name,
            user.email,
            profile.coach_name,
            profile.team_name,
            profile.team_role
        ])
        
        # Update profile_completed status
        profile.profile_completed = required_fields_filled
        profile.save()
        
        # Pass request context to serializer for building absolute URLs
        serializer = self.get_serializer(profile, context={'request': request})
        return Response({
            'message': 'Profile updated successfully',
            'profile': serializer.data
        })
    
    # Custom Endpoint: POST /api/profiles/upload-picture/
    @action(detail=False, methods=['post'], url_path='upload-picture')
    def upload_picture(self, request):
        """Upload profile picture"""
        profile = get_object_or_404(Profile, user=request.user)
        
        if 'profile_picture' not in request.FILES:
            return Response({
                'error': 'No picture file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        
        # Build absolute URL for profile picture
        picture_url = None
        if profile.profile_picture:
            picture_url = request.build_absolute_uri(profile.profile_picture.url)
        
        return Response({
            'message': 'Profile picture uploaded successfully',
            'profile_picture_url': picture_url
        })

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


# --- Authentication Views ---
class RegisterView(APIView):
    """POST /api/auth/register/ - User registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            username = request.data.get('username')  # Added username field
            email = request.data.get('email')
            password = request.data.get('password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            phone = request.data.get('phone', '')
            school = request.data.get('school', '')
            user_type = request.data.get('user_type', 'student')  # coach or student
            
            # Validation
            if not email or not password:
                return Response(
                    {'message': 'Email and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If username not provided, use email as username (backward compatibility)
            if not username:
                username = email
            
            # Check if user already exists (by email or username)
            if User.objects.filter(email=email).exists():
                return Response(
                    {'message': 'User with this email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(username=username).exists():
                return Response(
                    {'message': 'User with this username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create user
            user = User.objects.create_user(
                username=username,  # Use provided username or email
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create or update profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.school = school
            profile.user_type = user_type
            if user_type == 'coach':
                profile.role = 'team_manager'
            profile.save()
            
            # Generate token
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user_type
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'message': f'Registration failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    """POST /api/auth/login/ - User login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Accept both 'username' and 'email' fields
            username_or_email = request.data.get('username') or request.data.get('email')
            password = request.data.get('password')
            
            if not username_or_email or not password:
                return Response(
                    {'error': 'Username/Email and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Try to authenticate with username first
            user = authenticate(username=username_or_email, password=password)
            
            # If authentication failed, try to find user by email and authenticate
            if user is None:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is None:
                return Response(
                    {'error': 'Invalid username/email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get or create token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Get profile
            profile = Profile.objects.filter(user=user).first()
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': profile.user_type if profile else 'student',
                    'role': profile.role if profile else None
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'message': f'Login failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =============================================================================
# TOURNAMENT MANAGEMENT VIEWS
# =============================================================================

from .models import (
    Tournament, Team, Player, Match, Field, SpiritScore,
    Attendance, TournamentAnnouncement, VisitorRegistration
)
from .serializers import (
    TournamentSerializer, TeamSerializer, PlayerSerializer, MatchSerializer,
    FieldSerializer, SpiritScoreSerializer, AttendanceSerializer,
    TournamentAnnouncementSerializer, VisitorRegistrationSerializer
)
from django.db.models import Q, Count, Avg, F, Min, Max


# --- Tournament ViewSet ---
class TournamentViewSet(viewsets.ModelViewSet):
    """CRUD for Tournaments with custom actions"""
    serializer_class = TournamentSerializer
    permission_classes = [AllowAny]  # Public access to view tournaments
    queryset = Tournament.objects.all()
    
    def get_queryset(self):
        queryset = Tournament.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-start_date')
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get tournament leaderboard (team standings)"""
        tournament = self.get_object()
        teams = tournament.teams.filter(status='approved').order_by(
            '-wins', '-spirit_score_average', 'losses'
        )
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def spirit_rankings(self, request, pk=None):
        """Get spirit score rankings for tournament"""
        tournament = self.get_object()
        teams = tournament.teams.filter(status='approved').order_by(
            '-spirit_score_average', '-wins'
        )
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Get match schedule for tournament"""
        tournament = self.get_object()
        matches = tournament.matches.all().order_by('match_date', 'start_time')
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get tournament statistics"""
        tournament = self.get_object()
        
        players = Player.objects.filter(tournament=tournament)
        teams = Team.objects.filter(tournament=tournament, status='approved')
        matches = Match.objects.filter(tournament=tournament)
        
        stats = {
            'total_teams': teams.count(),
            'total_players': players.count(),
            'total_matches': matches.count(),
            'completed_matches': matches.filter(status='completed').count(),
            'average_spirit_score': teams.aggregate(avg=Avg('spirit_score_average'))['avg'] or 0,
            'gender_distribution': {
                'male': players.filter(gender='male').count(),
                'female': players.filter(gender='female').count(),
                'non_binary': players.filter(gender='non_binary').count(),
            },
            'age_stats': {
                'youngest': players.aggregate(min=Min('age'))['min'],
                'oldest': players.aggregate(max=Max('age'))['max'],
                'average': players.aggregate(avg=Avg('age'))['avg'],
            }
        }
        
        return Response(stats)


# --- Team ViewSet ---
class TeamViewSet(viewsets.ModelViewSet):
    """CRUD for Teams"""
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Team.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset.order_by('-wins', '-spirit_score_average')
    
    @action(detail=True, methods=['get'])
    def roster(self, request, pk=None):
        """Get team roster (players)"""
        team = self.get_object()
        players = team.players.all().order_by('jersey_number')
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get all matches for this team"""
        team = self.get_object()
        matches = Match.objects.filter(
            Q(team_a=team) | Q(team_b=team)
        ).order_by('match_date', 'start_time')
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)


# --- Player ViewSet ---
class PlayerViewSet(viewsets.ModelViewSet):
    """CRUD for Players"""
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Player.objects.all()
        team_id = self.request.query_params.get('team', None)
        tournament_id = self.request.query_params.get('tournament', None)
        
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
            
        return queryset.order_by('team__name', 'jersey_number')


# --- Match ViewSet ---
class MatchViewSet(viewsets.ModelViewSet):
    """CRUD for Matches with live scoring"""
    serializer_class = MatchSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Match.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        status = self.request.query_params.get('status', None)
        
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('match_date', 'start_time')
    
    @action(detail=True, methods=['post'])
    def update_score(self, request, pk=None):
        """Update match score (for live scoring)"""
        match = self.get_object()
        team_a_score = request.data.get('team_a_score')
        team_b_score = request.data.get('team_b_score')
        
        if team_a_score is not None:
            match.team_a_score = team_a_score
        if team_b_score is not None:
            match.team_b_score = team_b_score
            
        match.save()
        serializer = self.get_serializer(match)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark match as completed and update team stats"""
        match = self.get_object()
        match.status = 'completed'
        match.save()
        
        # Update team stats
        if match.team_a_score > match.team_b_score:
            match.team_a.wins += 1
            match.team_b.losses += 1
        elif match.team_b_score > match.team_a_score:
            match.team_b.wins += 1
            match.team_a.losses += 1
        else:
            match.team_a.draws += 1
            match.team_b.draws += 1
        
        match.team_a.points_for += match.team_a_score
        match.team_a.points_against += match.team_b_score
        match.team_b.points_for += match.team_b_score
        match.team_b.points_against += match.team_a_score
        
        match.team_a.save()
        match.team_b.save()
        
        serializer = self.get_serializer(match)
        return Response(serializer.data)


# --- Spirit Score ViewSet ---
class SpiritScoreViewSet(viewsets.ModelViewSet):
    """CRUD for Spirit Scores"""
    serializer_class = SpiritScoreSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = SpiritScore.objects.all()
        match_id = self.request.query_params.get('match', None)
        team_id = self.request.query_params.get('team', None)
        
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        if team_id:
            queryset = queryset.filter(Q(scoring_team_id=team_id) | Q(receiving_team_id=team_id))
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Auto-calculate total score and mark as submitted"""
        serializer.save(is_submitted=True, submitted_by=self.request.user if self.request.user.is_authenticated else None)


# --- Field ViewSet ---
class FieldViewSet(viewsets.ModelViewSet):
    """CRUD for Fields"""
    serializer_class = FieldSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Field.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset


# --- Attendance ViewSet ---
class AttendanceViewSet(viewsets.ModelViewSet):
    """CRUD for Attendance"""
    serializer_class = AttendanceSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Attendance.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        match_id = self.request.query_params.get('match', None)
        player_id = self.request.query_params.get('player', None)
        
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        if player_id:
            queryset = queryset.filter(player_id=player_id)
            
        return queryset.order_by('-date')


# --- Tournament Announcement ViewSet ---
class TournamentAnnouncementViewSet(viewsets.ModelViewSet):
    """CRUD for Tournament Announcements"""
    serializer_class = TournamentAnnouncementSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = TournamentAnnouncement.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset.order_by('-created_at')


# --- Visitor Registration ViewSet ---
class VisitorRegistrationViewSet(viewsets.ModelViewSet):
    """CRUD for Visitor Registration"""
    serializer_class = VisitorRegistrationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = VisitorRegistration.objects.all()
        tournament_id = self.request.query_params.get('tournament', None)
        if tournament_id:
            queryset = queryset.filter(tournament_id=tournament_id)
        return queryset.order_by('-registered_at')


# --- Additional Helper Views for Student Dashboard ---
class ProfileCheckCompletionView(APIView):
    """GET /api/profiles/check-completion/ - Check if profile is complete"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        profile = Profile.objects.filter(user=request.user).first()
        if not profile:
            return Response({'profile_completed': False})
        
        return Response({
            'profile_completed': profile.profile_completed,
            'user_type': profile.user_type,
            'role': profile.role
        })


class StudentFitnessView(APIView):
    """GET /api/student/fitness/ - Get student fitness data"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Mock fitness data - replace with actual Google Fit integration
        from datetime import datetime, timedelta
        import random
        
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
        
        # Generate mock data
        calories = [random.randint(1000, 2000) for _ in range(7)]
        steps = [random.randint(3000, 10000) for _ in range(7)]
        active_minutes = [random.randint(20, 120) for _ in range(7)]
        
        return Response({
            'today': {
                'calories': calories[-1],
                'steps': steps[-1],
                'active_minutes': active_minutes[-1]
            },
            'calories': calories,
            'steps': steps,
            'active_minutes': active_minutes,
            'dates': dates
        })


class StudentScheduleView(APIView):
    """GET /api/student/schedule/ - Get student schedule"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Return matches for the student's team
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or not profile.team_name:
            return Response([])
        
        # Find teams matching the student's team name
        from .models import Team, Match
        teams = Team.objects.filter(name__icontains=profile.team_name)
        
        if not teams.exists():
            return Response([])
        
        # Get matches for these teams
        team_ids = teams.values_list('id', flat=True)
        matches = Match.objects.filter(
            Q(team1_id__in=team_ids) | Q(team2_id__in=team_ids)
        ).order_by('scheduled_time')[:10]
        
        schedule_data = []
        for match in matches:
            schedule_data.append({
                'id': match.id,
                'date': match.scheduled_time.strftime('%Y-%m-%d'),
                'time': match.scheduled_time.strftime('%H:%M'),
                'team1': match.team1.name if match.team1 else 'TBD',
                'team2': match.team2.name if match.team2 else 'TBD',
                'field': match.field.name if match.field else 'TBD',
                'status': match.status
            })
        
        return Response(schedule_data)


class LeaderboardView(APIView):
    """GET /api/leaderboard/ - Get global leaderboard across all tournaments"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        from .models import Team
        from django.db.models import Avg
        
        # Get all teams sorted by wins
        teams = Team.objects.annotate(
            avg_spirit=Avg('received_spirit_scores__total_score')
        ).order_by('-wins', '-points', '-avg_spirit')[:20]
        
        leaderboard_data = []
        for team in teams:
            leaderboard_data.append({
                'id': team.id,
                'name': team.name,
                'city': team.home_city,
                'wins': team.wins,
                'losses': team.losses,
                'draws': team.draws,
                'points': team.points,
                'points_for': team.points_for,
                'points_against': team.points_against,
                'point_differential': team.points_for - team.points_against,
                'average_spirit_score': float(team.spirit_score_average) if team.spirit_score_average else 0.0,
                'logo_url': team.logo.url if team.logo else None,
                'players': [{
                    'id': p.id,
                    'name': p.full_name,
                    'jersey_number': p.jersey_number,
                    'position': p.position,
                    'is_active': p.is_active
                } for p in team.players.all()[:8]]
            })
        
        return Response(leaderboard_data)


# ===================== Google OAuth Views =====================

class GoogleOAuthView(APIView):
    """
    GET /api/auth/google/ - Initiate Google OAuth flow
    GET /api/auth/google/callback/ - Handle Google OAuth callback
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Initiate Google OAuth flow
        Returns the Google OAuth authorization URL
        """
        import os
        from urllib.parse import urlencode
        
        # Google OAuth 2.0 endpoints
        google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        
        # Get Google OAuth credentials from environment
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:8000/api/auth/google/callback/')
        
        # If no credentials, return mock response for development
        if not client_id:
            # Return a development mode response
            return Response({
                'auth_url': None,
                'message': 'Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file.',
                'dev_mode': True
            })
        
        # OAuth parameters with Google Fit scopes
        scopes = [
            'openid',
            'email',
            'profile',
            'https://www.googleapis.com/auth/fitness.activity.read',  # Read activity data
            'https://www.googleapis.com/auth/fitness.body.read',      # Read body measurements
            'https://www.googleapis.com/auth/fitness.location.read',  # Read location data
        ]
        
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),  # Space-separated scopes
            'access_type': 'offline',  # Get refresh token
            'prompt': 'consent'  # Always show consent screen
        }
        
        # Build authorization URL
        auth_url = f"{google_auth_url}?{urlencode(params)}"
        
        return Response({
            'auth_url': auth_url,
            'dev_mode': False
        })


class GoogleOAuthCallbackView(APIView):
    """
    Handle Google OAuth callback
    Creates or updates user account and returns token
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Handle OAuth callback from Google"""
        import os
        import requests
        from urllib.parse import urlencode
        
        # Get authorization code from query params
        code = request.GET.get('code')
        error = request.GET.get('error')
        
        if error:
            return Response({
                'error': f'Google authentication failed: {error}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not code:
            return Response({
                'error': 'No authorization code provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get Google OAuth credentials
        client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:8000/api/auth/google/callback/')
        
        if not client_id or not client_secret:
            return Response({
                'error': 'Google OAuth not configured on server'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Exchange code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        try:
            # Debug logging
            print(f"DEBUG: Exchanging code with Google...")
            print(f"DEBUG: client_id = {client_id[:20]}...")
            print(f"DEBUG: client_secret = {client_secret[:15]}...")
            print(f"DEBUG: redirect_uri = {redirect_uri}")
            
            token_response = requests.post(token_url, data=token_data)
            token_json = token_response.json()
            
            # Debug logging
            print(f"DEBUG: Google response status = {token_response.status_code}")
            print(f"DEBUG: Google response = {token_json}")
            
            if 'error' in token_json:
                return Response({
                    'error': f"Token exchange failed: {token_json.get('error_description', token_json.get('error', 'Unknown error'))}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            access_token = token_json.get('access_token')
            refresh_token = token_json.get('refresh_token')  # Save refresh token
            
            # Get user info from Google
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            userinfo_response = requests.get(userinfo_url, headers=headers)
            user_info = userinfo_response.json()
            
            # Extract user data
            email = user_info.get('email')
            first_name = user_info.get('given_name', '')
            last_name = user_info.get('family_name', '')
            google_id = user_info.get('id')
            
            if not email:
                return Response({
                    'error': 'Could not retrieve email from Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user exists
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )
            
            # Create or update profile
            profile, profile_created = Profile.objects.get_or_create(user=user)
            
            # Update profile with Google info
            profile.google_email = email
            profile.google_id = google_id
            profile.google_access_token = access_token
            profile.google_refresh_token = refresh_token  # Store refresh token for later use
            
            # Determine user type from the state or set default
            # Check if user came from student or coach registration
            # For now, check the referrer or set based on existing profile
            if created or not profile.user_type:
                # Default to student if registering via Google
                # (Coach registration typically uses manual form)
                profile.user_type = 'student'
                profile.role = 'player'
            
            profile.save()
            
            # Generate or get auth token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Redirect based on user type
            from django.shortcuts import redirect
            if profile.user_type == 'coach':
                redirect_url = f"http://localhost:3000/coach/dashboard?token={token.key}&google_connected=true&first_time={'true' if created else 'false'}"
            else:
                redirect_url = f"http://localhost:3000/student/home?token={token.key}&google_connected=true&first_time={'true' if created else 'false'}"
            
            return redirect(redirect_url)
            
        except requests.RequestException as e:
            return Response({
                'error': f'Failed to communicate with Google: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'error': f'Authentication failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===================== Google Fit API Views =====================

class GoogleFitDataView(APIView):
    """
    GET /api/fitness/google-fit/ - Fetch fitness data from Google Fit
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Fetch fitness data from Google Fit API"""
        import os
        import requests
        from datetime import datetime, timedelta
        
        # Get user's profile
        profile = get_object_or_404(Profile, user=request.user)
        
        # Check if user has connected Google account
        if not profile.google_access_token:
            return Response({
                'error': 'Google account not connected. Please login with Google first.',
                'google_connected': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = profile.google_access_token
        
        # Get date range (last 7 days by default)
        days = int(request.GET.get('days', 7))
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Convert to milliseconds (Google Fit uses milliseconds)
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        
        try:
            # Google Fit API endpoint
            fit_api_url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Request body for aggregated data
            data = {
                "aggregateBy": [
                    {
                        "dataTypeName": "com.google.step_count.delta",
                        "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
                    },
                    {
                        "dataTypeName": "com.google.calories.expended",
                        "dataSourceId": "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
                    },
                    {
                        "dataTypeName": "com.google.distance.delta",
                        "dataSourceId": "derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta"
                    },
                    {
                        "dataTypeName": "com.google.heart_rate.bpm",
                        "dataSourceId": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
                    }
                ],
                "bucketByTime": {"durationMillis": 86400000},  # 1 day in milliseconds
                "startTimeMillis": start_time_ms,
                "endTimeMillis": end_time_ms
            }
            
            # Make request to Google Fit API
            response = requests.post(fit_api_url, headers=headers, json=data)
            
            if response.status_code == 401:
                # Token expired, need to re-authenticate
                return Response({
                    'error': 'Google access token expired. Please reconnect your Google account.',
                    'google_connected': False,
                    'token_expired': True
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not response.ok:
                return Response({
                    'error': f'Failed to fetch Google Fit data: {response.text}',
                    'status_code': response.status_code
                }, status=status.HTTP_400_BAD_REQUEST)
            
            fit_data = response.json()
            
            # Process and format the data
            formatted_data = self.process_fit_data(fit_data)
            
            return Response({
                'google_connected': True,
                'date_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'days': days
                },
                'fitness_data': formatted_data,
                'summary': self.calculate_summary(formatted_data)
            })
            
        except requests.RequestException as e:
            return Response({
                'error': f'Failed to communicate with Google Fit: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'error': f'Error fetching fitness data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def process_fit_data(self, raw_data):
        """Process raw Google Fit data into readable format"""
        processed_data = []
        
        for bucket in raw_data.get('bucket', []):
            date_data = {
                'date': datetime.fromtimestamp(int(bucket['startTimeMillis']) / 1000).strftime('%Y-%m-%d'),
                'steps': 0,
                'calories': 0,
                'distance': 0,
                'heart_rate': []
            }
            
            for dataset in bucket.get('dataset', []):
                data_type = dataset.get('dataSourceId', '')
                
                for point in dataset.get('point', []):
                    for value in point.get('value', []):
                        if 'step_count' in data_type:
                            date_data['steps'] += int(value.get('intVal', 0))
                        elif 'calories' in data_type:
                            date_data['calories'] += round(value.get('fpVal', 0), 2)
                        elif 'distance' in data_type:
                            date_data['distance'] += round(value.get('fpVal', 0) / 1000, 2)  # Convert to km
                        elif 'heart_rate' in data_type:
                            date_data['heart_rate'].append(round(value.get('fpVal', 0), 1))
            
            # Calculate average heart rate
            if date_data['heart_rate']:
                date_data['avg_heart_rate'] = round(sum(date_data['heart_rate']) / len(date_data['heart_rate']), 1)
            else:
                date_data['avg_heart_rate'] = 0
            
            del date_data['heart_rate']  # Remove raw heart rate data
            processed_data.append(date_data)
        
        return processed_data
    
    def calculate_summary(self, fitness_data):
        """Calculate summary statistics"""
        if not fitness_data:
            return {
                'total_steps': 0,
                'total_calories': 0,
                'total_distance': 0,
                'avg_steps_per_day': 0,
                'avg_calories_per_day': 0
            }
        
        total_steps = sum(day['steps'] for day in fitness_data)
        total_calories = sum(day['calories'] for day in fitness_data)
        total_distance = sum(day['distance'] for day in fitness_data)
        days_count = len(fitness_data)
        
        return {
            'total_steps': total_steps,
            'total_calories': round(total_calories, 2),
            'total_distance': round(total_distance, 2),
            'avg_steps_per_day': round(total_steps / days_count, 0) if days_count > 0 else 0,
            'avg_calories_per_day': round(total_calories / days_count, 2) if days_count > 0 else 0,
            'avg_distance_per_day': round(total_distance / days_count, 2) if days_count > 0 else 0
        }