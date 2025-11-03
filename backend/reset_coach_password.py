import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User

print("\n🔑 RESET COACH PASSWORD\n")

username = input("Enter coach username: ").strip()

try:
    user = User.objects.get(username=username)
    print(f"\n✅ Found user: {user.username} ({user.email})")
    
    new_password = input("Enter new password: ").strip()
    
    if len(new_password) < 4:
        print("\n❌ Password too short! Use at least 4 characters.")
    else:
        user.set_password(new_password)
        user.save()
        print(f"\n✅ Password updated successfully for {username}!")
        print(f"\n🎯 You can now login at: http://localhost:3000/coach/login")
        print(f"   Username: {username}")
        print(f"   Password: {new_password}\n")
except User.DoesNotExist:
    print(f"\n❌ User '{username}' not found!")
    print("\nAvailable coach usernames:")
    from api.models import Profile
    coaches = Profile.objects.filter(user_type='coach')
    for coach in coaches:
        print(f"  - {coach.user.username}")
    print()
