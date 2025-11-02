import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Profile

print("\n" + "="*80)
print("COACH DATABASE RECORDS")
print("="*80 + "\n")

# Get all profiles with user_type = 'coach' or role = 'team_manager'
coaches = Profile.objects.filter(
    user_type__in=['coach', 'team_manager']
) | Profile.objects.filter(
    role__in=['coach', 'team_manager']
)

coaches = coaches.distinct()

if coaches.count() == 0:
    print("❌ No coaches found in the database yet.")
    print("\nTry registering a coach at: http://localhost:3000/coach/register\n")
else:
    print(f"✅ Found {coaches.count()} coach(es) in the database:\n")
    
    for idx, profile in enumerate(coaches, 1):
        user = profile.user
        print(f"Coach #{idx}")
        print("-" * 60)
        print(f"  ID: {profile.id}")
        print(f"  User ID: {user.id}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Email: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Phone: {profile.phone or 'Not provided'}")
        print(f"  Team Name: {profile.team_name or 'Not provided'}")
        print(f"  Coach Name: {profile.coach_name or 'Not provided'}")
        print(f"  School: {profile.school or 'Not provided'}")
        print(f"  User Type: {profile.user_type or 'Not set'}")
        print(f"  Role: {profile.role or 'Not set'}")
        print(f"  Profile Completed: {profile.profile_completed}")
        print(f"  Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
        print("-" * 60)
        print()

print("="*80)
print("\nTo view all users (including students):")
print("  python check_profiles.py")
print("="*80 + "\n")
