#!/usr/bin/env python
"""
Database Checker Script
Shows all important data in the database: users, coaches, students, teams, tournaments, etc.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import (
    Profile, Tournament, Team, Player, Match, 
    SpiritScore, Attendance, Field
)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_users():
    """Check all users and their profiles"""
    print_header("USERS & PROFILES")
    
    users = User.objects.all()
    print(f"\nTotal Users: {users.count()}\n")
    
    if users.count() == 0:
        print("  No users found!")
        return
    
    for user in users:
        try:
            profile = user.profile
            print(f"👤 Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   User Type: {profile.user_type}")
            print(f"   Role: {profile.role or 'N/A'}")
            print(f"   Total Points: {profile.total_points}")
            print(f"   Profile Completed: {profile.profile_completed}")
            if profile.google_email:
                print(f"   Google Connected: ✓ ({profile.google_email})")
            print()
        except Profile.DoesNotExist:
            print(f"👤 Username: {user.username} (NO PROFILE)")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   ⚠️  Profile missing - creating...")
            Profile.objects.create(user=user)
            print(f"   ✓ Profile created!")
            print()

def check_coaches():
    """Check all coaches"""
    print_header("COACHES")
    
    coaches = Profile.objects.filter(user_type='coach')
    print(f"\nTotal Coaches: {coaches.count()}\n")
    
    if coaches.count() == 0:
        print("  No coaches found!")
        return
    
    for coach in coaches:
        print(f"🏅 {coach.user.first_name} {coach.user.last_name} (@{coach.user.username})")
        print(f"   Email: {coach.user.email}")
        print(f"   Role: {coach.role or 'N/A'}")
        print(f"   Coach Name: {coach.coach_name or 'N/A'}")
        print()

def check_students():
    """Check all students"""
    print_header("STUDENTS")
    
    students = Profile.objects.filter(user_type='student')
    print(f"\nTotal Students: {students.count()}\n")
    
    if students.count() == 0:
        print("  No students found!")
        return
    
    for student in students:
        print(f"🎓 {student.user.first_name} {student.user.last_name} (@{student.user.username})")
        print(f"   Email: {student.user.email}")
        print(f"   Role: {student.role or 'N/A'}")
        print(f"   Team: {student.team_name or 'N/A'}")
        print(f"   Team Role: {student.team_role or 'N/A'}")
        print(f"   School: {student.school or 'N/A'}")
        print(f"   Points: {student.total_points}")
        print()

def check_tournaments():
    """Check all tournaments"""
    print_header("TOURNAMENTS")
    
    tournaments = Tournament.objects.all()
    print(f"\nTotal Tournaments: {tournaments.count()}\n")
    
    if tournaments.count() == 0:
        print("  No tournaments found!")
        return
    
    for tournament in tournaments:
        print(f"🏆 {tournament.name}")
        print(f"   Status: {tournament.status}")
        print(f"   Format: {tournament.tournament_format}")
        print(f"   Location: {tournament.location}")
        print(f"   Dates: {tournament.start_date} to {tournament.end_date}")
        print(f"   Registration Deadline: {tournament.registration_deadline}")
        print(f"   Max Teams: {tournament.max_teams}")
        print(f"   Teams Registered: {tournament.teams.count()}")
        print(f"   Director: {tournament.tournament_director.username if tournament.tournament_director else 'N/A'}")
        print()

def check_teams():
    """Check all teams"""
    print_header("TEAMS")
    
    teams = Team.objects.all()
    print(f"\nTotal Teams: {teams.count()}\n")
    
    if teams.count() == 0:
        print("  No teams found!")
        return
    
    for team in teams:
        print(f"⚡ {team.name} ({team.tournament.name})")
        print(f"   Status: {team.status}")
        print(f"   Captain: {team.captain.username if team.captain else 'N/A'}")
        print(f"   Home City: {team.home_city}")
        print(f"   Record: {team.wins}W - {team.losses}L - {team.draws}D")
        print(f"   Points: {team.points_for} For, {team.points_against} Against")
        print(f"   Spirit Score Avg: {team.spirit_score_average:.2f}")
        print(f"   Players: {team.players.count()}")
        print()

def check_players():
    """Check all players"""
    print_header("PLAYERS")
    
    players = Player.objects.all()
    print(f"\nTotal Players: {players.count()}\n")
    
    if players.count() == 0:
        print("  No players found!")
        return
    
    for player in players:
        print(f"👟 {player.full_name} (#{player.jersey_number or 'N/A'})")
        print(f"   Team: {player.team.name}")
        print(f"   Tournament: {player.tournament.name}")
        print(f"   Email: {player.email}")
        print(f"   Position: {player.position or 'N/A'}")
        print(f"   Experience: {player.experience_level}")
        print(f"   Verified: {'✓' if player.is_verified else '✗'}")
        print()

def check_matches():
    """Check all matches"""
    print_header("MATCHES")
    
    matches = Match.objects.all()
    print(f"\nTotal Matches: {matches.count()}\n")
    
    if matches.count() == 0:
        print("  No matches found!")
        return
    
    for match in matches:
        print(f"⚔️  Match #{match.match_number} - Round {match.round_number}")
        print(f"   {match.team_a.name} vs {match.team_b.name}")
        print(f"   Score: {match.team_a_score} - {match.team_b_score}")
        print(f"   Status: {match.status}")
        print(f"   Date/Time: {match.match_date} at {match.start_time}")
        print(f"   Field: {match.field.name if match.field else 'N/A'}")
        winner = match.get_winner()
        if winner:
            print(f"   Winner: {winner.name}")
        print()

def check_spirit_scores():
    """Check all spirit scores"""
    print_header("SPIRIT SCORES")
    
    scores = SpiritScore.objects.filter(is_submitted=True)
    print(f"\nTotal Spirit Scores Submitted: {scores.count()}\n")
    
    if scores.count() == 0:
        print("  No spirit scores found!")
        return
    
    for score in scores:
        print(f"💫 {score.scoring_team.name} → {score.receiving_team.name}")
        print(f"   Match: {score.match}")
        print(f"   Total Score: {score.total_score}/20")
        print(f"   Rules Knowledge: {score.rules_knowledge}")
        print(f"   Fouls & Contact: {score.fouls_and_contact}")
        print(f"   Fair-mindedness: {score.fair_mindedness}")
        print(f"   Positive Attitude: {score.positive_attitude}")
        print(f"   Communication: {score.communication}")
        if score.comments:
            print(f"   Comments: {score.comments}")
        print()

def check_fields():
    """Check all fields"""
    print_header("FIELDS")
    
    fields = Field.objects.all()
    print(f"\nTotal Fields: {fields.count()}\n")
    
    if fields.count() == 0:
        print("  No fields found!")
        return
    
    for field in fields:
        print(f"🏟️  {field.name} ({field.tournament.name})")
        print(f"   Active: {'✓' if field.is_active else '✗'}")
        print(f"   Location: {field.location_details or 'N/A'}")
        print(f"   Matches: {field.matches.count()}")
        print()

def check_attendance():
    """Check attendance records"""
    print_header("ATTENDANCE")
    
    attendance = Attendance.objects.all()
    print(f"\nTotal Attendance Records: {attendance.count()}\n")
    
    if attendance.count() == 0:
        print("  No attendance records found!")
        return
    
    present_count = attendance.filter(is_present=True).count()
    absent_count = attendance.filter(is_present=False).count()
    
    print(f"   Present: {present_count}")
    print(f"   Absent: {absent_count}")
    print()
    
    # Show recent attendance
    recent = attendance.order_by('-date')[:10]
    if recent:
        print("Recent Attendance:")
        for att in recent:
            status = "Present ✓" if att.is_present else "Absent ✗"
            print(f"   {att.player.full_name} - {att.date} - {status}")
        print()

def main():
    """Main function to run all checks"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  DATABASE CHECKER - Hackathon WAME Backend".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    try:
        check_users()
        check_coaches()
        check_students()
        check_tournaments()
        check_teams()
        check_players()
        check_matches()
        check_spirit_scores()
        check_fields()
        check_attendance()
        
        print_header("DATABASE CHECK COMPLETE")
        print("\nAll database queries executed successfully! ✓\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
