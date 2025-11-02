# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router to handle ModelViewSet URLs (Profiles, Workouts, Exercises)
router = DefaultRouter()
router.register('profiles', views.ProfileViewSet, basename='profile')
router.register('workouts', views.WorkoutViewSet, basename='workout')
router.register('exercises', views.ExerciseViewSet, basename='exercise')
router.register('posture', views.PostureAnalysisViewSet, basename='analysis')

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
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # Google OAuth Endpoints
    path('auth/google/', views.GoogleLoginView.as_view(), name='google_login'),
    path('auth/google/callback/', views.GoogleCallbackView.as_view(), name='google_callback'),
    
    # Database Stats (for verification)
    path('db/stats/', views.DatabaseStatsView.as_view(), name='db_stats'),
    
    # Student Dashboard Endpoints
    path('student/fitness/', views.StudentFitnessView.as_view(), name='student_fitness'),
    path('student/fitness/sync-google-fit/', views.GoogleFitSyncView.as_view(), name='sync_google_fit'),
    path('student/schedule/', views.StudentScheduleView.as_view(), name='student_schedule'),
    
    # Admin/Coach Endpoints
    path('admin/students-fitness/', views.AllStudentsFitnessView.as_view(), name='all_students_fitness'),
    
    # Tournament Endpoints
    path('tournaments/', views.TournamentListView.as_view(), name='tournaments'),
    path('tournaments/<int:tournament_id>/register/', views.TournamentRegisterView.as_view(), name='tournament_register'),
    
    # Leaderboard
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    
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

    # Donation Endpoint
    path('donate/', views.DonateView.as_view(), name='donate'),
]