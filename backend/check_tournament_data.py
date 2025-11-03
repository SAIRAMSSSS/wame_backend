import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Profile

print("="*70)
print("🔍 CHECKING DATABASE FOR TOURNAMENT-RELATED DATA")
print("="*70)

# Check for users
all_users = User.objects.all()
print(f"\n📊 Total Users: {all_users.count()}")

# Check for specific tournament users
tournament_usernames = ['director', 'captain1', 'captain2', 'captain3', 'captain4']
print("\n👥 Checking for Tournament Users:")
for username in tournament_usernames:
    user = User.objects.filter(username=username).first()
    if user:
        print(f"  ✅ Found: {username}")
        profile = Profile.objects.filter(user=user).first()
        if profile:
            print(f"     - Email: {user.email}")
            print(f"     - Profile exists: Yes")
    else:
        print(f"  ❌ Not found: {username}")

# Check all users
print("\n📋 All Users in Database:")
for user in all_users:
    profile = Profile.objects.filter(user=user).first()
    print(f"  • {user.username} ({user.email})")
    if profile:
        print(f"    - Has profile: Yes")
        if hasattr(profile, 'user_type'):
            print(f"    - User type: {profile.user_type}")
        if hasattr(profile, 'role'):
            print(f"    - Role: {profile.role}")

# Check for Tournament model
print("\n🏆 Checking for Tournament Models:")
try:
    from django.apps import apps
    app_models = apps.get_app_config('api').get_models()
    model_names = [model.__name__ for model in app_models]
    print(f"  Available models in 'api' app: {', '.join(model_names)}")
    
    # Check if Tournament, Team, Player models exist
    tournament_models = ['Tournament', 'Team', 'Player', 'Match']
    for model_name in tournament_models:
        if model_name in model_names:
            print(f"  ✅ {model_name} model exists")
        else:
            print(f"  ❌ {model_name} model NOT found")
except Exception as e:
    print(f"  ❌ Error checking models: {e}")

print("\n" + "="*70)
print("✅ CHECK COMPLETE")
print("="*70)
