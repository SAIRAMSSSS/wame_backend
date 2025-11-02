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

    # Phone Login Endpoints
    path('auth/send_otp/', views.PhoneLoginView.as_view(), name='send_otp'),
    path('auth/verify_otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
]