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
print("🔑 COACH LOGIN CREDENTIALS")
print("="*80 + "\n")

# Get all profiles with user_type = 'coach' or role = 'team_manager'
coaches = Profile.objects.filter(
    user_type__in=['coach', 'team_manager']
) | Profile.objects.filter(
    role__in=['coach', 'team_manager']
)

coaches = coaches.distinct()

if coaches.count() == 0:
    print("❌ No coaches found in the database yet.\n")
else:
    print(f"✅ Found {coaches.count()} coach(es). You can login with these:\n")
    
    for idx, profile in enumerate(coaches, 1):
        user = profile.user
        print(f"Coach #{idx}")
        print("-" * 60)
        print(f"  📧 Email: {user.email}")
        print(f"  👤 Name: {user.first_name} {user.last_name}")
        print(f"  🏫 School: {profile.school or 'Not set'}")
        print(f"  🏆 Team: {profile.team_name or 'Not set'}")
        print(f"  🔐 Password: (the password you set during registration)")
        print(f"  📝 Note: Login at http://localhost:3000/coach/login")
        print("-" * 60)
        print()

print("\n💡 TIP: If you don't know the password for test coaches,")
print("   register a new coach at: http://localhost:3000/coach/register")
print("\n" + "="*80 + "\n")
