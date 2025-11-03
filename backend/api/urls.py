# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router to handle ModelViewSet URLs (Profiles, Workouts, Exercises, Tournaments)
router = DefaultRouter()
router.register('profiles', views.ProfileViewSet, basename='profile')
router.register('workouts', views.WorkoutViewSet, basename='workout')
router.register('exercises', views.ExerciseViewSet, basename='exercise')
router.register('posture', views.PostureAnalysisViewSet, basename='analysis')

# Tournament Management Routes
router.register('tournaments', views.TournamentViewSet, basename='tournament')
router.register('teams', views.TeamViewSet, basename='team')
router.register('players', views.PlayerViewSet, basename='player')
router.register('matches', views.MatchViewSet, basename='match')
router.register('fields', views.FieldViewSet, basename='field')
router.register('spirit-scores', views.SpiritScoreViewSet, basename='spirit-score')
router.register('attendance', views.AttendanceViewSet, basename='attendance')
router.register('announcements', views.TournamentAnnouncementViewSet, basename='announcement')
router.register('visitors', views.VisitorRegistrationViewSet, basename='visitor')

# The main URL patterns for your 'api' app
urlpatterns = [
    # 1. Router URLs (e.g., /api/profiles/, /api/workouts/1/complete/)
    path('', include(router.urls)), 
    
    # 2. Specific APIView URLs (Must be defined explicitly before the router includes catch-alls)
    
    # Health Check
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # Authentication Endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/google/', views.GoogleOAuthView.as_view(), name='google_oauth'),
    path('auth/google/callback/', views.GoogleOAuthCallbackView.as_view(), name='google_oauth_callback'),
    
    # Student Dashboard Endpoints
    path('student/fitness/', views.StudentFitnessView.as_view(), name='student_fitness'),
    path('student/schedule/', views.StudentScheduleView.as_view(), name='student_schedule'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    
    # Google Fit Integration
    path('fitness/google-fit/', views.GoogleFitDataView.as_view(), name='google_fit_data'),
    
    # Posture Analysis Endpoints
    # Note: These views handle the POST requests for file analysis
    path('posture/analyze_image/', views.AnalyzeImageView.as_view(), name='analyze_image'),
    # Assuming analyze_video uses similar processing logic, otherwise create a separate view
    path('posture/analyze_video/', views.AnalyzeImageView.as_view(), name='analyze_video'), 
    
    # Recommendation Endpoints
    # The /recommendations/ endpoint will map to the GET method in RecommendationView
    path('recommendations/', views.RecommendationView.as_view(), name='list_recommendations'),
    # The /recommendations/generate/ endpoint will map to the POST method
    path('recommendations/generate/', views.RecommendationView.as_view(), name='generate_recommendations'),
]