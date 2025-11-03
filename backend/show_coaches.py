import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Profile

print("\n" + "="*60)
print("🏀 COACH ACCOUNTS IN DATABASE")
print("="*60 + "\n")

# Get all coach profiles
coaches = Profile.objects.filter(user_type='coach')

if not coaches.exists():
    print("❌ No coach accounts found in the database.\n")
    print("💡 You can create a coach account by:")
    print("   1. Register at: http://localhost:3000/coach/register")
    print("   2. Or use Django admin: http://127.0.0.1:8000/admin/\n")
else:
    for i, profile in enumerate(coaches, 1):
        print(f"Coach #{i}:")
        print(f"  👤 Username: {profile.user.username}")
        print(f"  📧 Email: {profile.user.email}")
        print(f"  📛 Name: {profile.user.first_name} {profile.user.last_name}")
        print(f"  🏫 Team: {profile.team_name or 'Not set'}")
        print(f"  🔑 Password: *** (hashed - cannot display)")
        print(f"  ℹ️  User Type: {profile.user_type}")
        print(f"  📝 Role: {profile.role or 'Not set'}")
        print("-" * 60 + "\n")

print("\n💡 NEED TO RESET PASSWORD?")
print("   You can reset password in Django Admin:")
print("   1. Go to: http://127.0.0.1:8000/admin/")
print("   2. Login with superuser credentials")
print("   3. Click 'Users' → Select coach → Change password\n")

print("📌 OR CREATE NEW COACH:")
print("   Register at: http://localhost:3000/coach/register\n")
