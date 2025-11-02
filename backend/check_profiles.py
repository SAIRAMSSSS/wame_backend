#!/usr/bin/env python
"""
Quick script to check all user profiles in the database
Run with: python check_profiles.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from api.models import Profile
from django.contrib.auth.models import User

def check_profiles():
    print("\n" + "="*80)
    print("USER PROFILES IN DATABASE")
    print("="*80 + "\n")
    
    profiles = Profile.objects.all()
    
    if not profiles.exists():
        print("❌ No profiles found in database!\n")
        return
    
    print(f"Total Profiles: {profiles.count()}\n")
    
    for i, profile in enumerate(profiles, 1):
        user = profile.user
        print(f"{'='*80}")
        print(f"Profile #{i}")
        print(f"{'='*80}")
        print(f"👤 Username:        {user.username}")
        print(f"📧 Email:           {user.email}")
        print(f"📝 First Name:      {user.first_name or '(not set)'}")
        print(f"📝 Last Name:       {user.last_name or '(not set)'}")
        print(f"\n🏈 TEAM INFORMATION:")
        print(f"   Coach Name:      {profile.coach_name or '(not set)'}")
        print(f"   Team Name:       {profile.team_name or '(not set)'}")
        print(f"   Team Role:       {profile.team_role or '(not set)'}")
        print(f"\n📊 OTHER INFO:")
        print(f"   User Type:       {profile.user_type}")
        print(f"   Phone:           {profile.phone or '(not set)'}")
        print(f"   Age:             {profile.age or '(not set)'}")
        print(f"   School:          {profile.school or '(not set)'}")
        print(f"   Total Points:    {profile.total_points}")
        print(f"   Profile Picture: {profile.profile_picture.url if profile.profile_picture else '(not set)'}")
        print(f"\n✅ Profile Status:")
        print(f"   Completed:       {'✅ YES' if profile.profile_completed else '❌ NO'}")
        
        if profile.google_email:
            print(f"\n🔗 GOOGLE OAUTH:")
            print(f"   Google Email:    {profile.google_email}")
            print(f"   Google ID:       {profile.google_id}")
        
        print("\n")
    
    # Summary
    completed = profiles.filter(profile_completed=True).count()
    incomplete = profiles.filter(profile_completed=False).count()
    
    print(f"{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Completed Profiles: {completed}")
    print(f"❌ Incomplete Profiles: {incomplete}")
    print(f"\n")

if __name__ == '__main__':
    check_profiles()
