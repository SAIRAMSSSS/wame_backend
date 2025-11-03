"""
Simple script to populate tournament data
Run with: python populate_data.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Profile, Tournament, Team, Player, Match, Field, SpiritScore, TournamentAnnouncement
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

print('🚀 Starting tournament data population...\n')

# Create tournament
tournament, created = Tournament.objects.get_or_create(
    name='Y-Ultimate Championship 2025',
    defaults={
        'description': 'The premier Ultimate Frisbee tournament featuring top teams from across India.',
        'location': 'Jawaharlal Nehru Stadium, Delhi',
        'start_date': timezone.now().date(),
        'end_date': (timezone.now() + timedelta(days=3)).date(),
        'registration_deadline': (timezone.now() - timedelta(days=7)).date(),
        'status': 'ongoing',
        'tournament_format': 'round_robin',
        'max_teams': 8,
        'rules': 'Standard WFDF rules apply',
        'sponsors': 'Nike, Adidas, Red Bull'
    }
)
print(f'✅ Tournament: {tournament.name}')

# Create fields
fields = []
for i, (name, loc) in enumerate([('Field A', 'North'), ('Field B', 'South'), ('Field C', 'East')]):
    field, _ = Field.objects.get_or_create(
        tournament=tournament,
        name=name,
        defaults={'location_details': loc, 'is_active': True}
    )
    fields.append(field)
print(f'✅ Created {len(fields)} fields')

# Create teams
teams_info = [
    ('Mumbai Thunderbolts', 'Mumbai', 'captain1', 'Raj', 'Sharma'),
    ('Delhi Dynamos', 'Delhi', 'captain2', 'Priya', 'Singh'),
    ('Bangalore Blaze', 'Bangalore', 'captain3', 'Arjun', 'Patel'),
    ('Pune Phoenix', 'Pune', 'captain4', 'Neha', 'Gupta'),
]

teams = []
for team_name, city, username, first, last in teams_info:
    # Create captain user
    captain, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@yultimate.com', 'first_name': first, 'last_name': last}
    )
    if created:
        captain.set_password('password123')
        captain.save()
        Token.objects.create(user=captain)
    
    # Create team
    team, _ = Team.objects.get_or_create(
        tournament=tournament,
        name=team_name,
        defaults={
            'captain': captain,
            'home_city': city,
            'status': 'approved',
            'wins': 0,
            'losses': 0,
            'points_for': 0,
            'points_against': 0
        }
    )
    teams.append(team)
    
    # Create 8 players per team
    names = ['Amit Kumar', 'Sneha Reddy', 'Vikram Iyer', 'Pooja Joshi', 
             'Rahul Verma', 'Anjali Nair', 'Karan Chopra', 'Meera Desai']
    positions = ['Handler', 'Cutter', 'Hybrid', 'Deep'] * 2
    
    for i, (full_name, pos) in enumerate(zip(names, positions)):
        Player.objects.get_or_create(
            team=team,
            email=f'{full_name.lower().replace(" ", ".")}@yultimate.com',
            defaults={
                'tournament': tournament,
                'full_name': full_name,
                'phone': f'+91-9876{i:05d}',
                'gender': 'male' if i % 2 == 0 else 'female',
                'age': 20 + i,
                'jersey_number': i + 1,
                'position': pos,
                'experience_level': 'advanced' if i < 4 else 'intermediate',
                'is_verified': True
            }
        )

print(f'✅ Created {len(teams)} teams with 8 players each')

# Create matches
match_count = 0
for i, team_a in enumerate(teams):
    for team_b in teams[i+1:]:
        is_completed = match_count < 3
        status = 'completed' if is_completed else 'scheduled'
        ta_score = 13 if is_completed and match_count % 2 == 0 else 10 if is_completed else 0
        tb_score = 10 if is_completed and match_count % 2 == 0 else 13 if is_completed else 0
        match_time = timezone.now() + timedelta(hours=match_count * 2)
        
        match, _ = Match.objects.get_or_create(
            tournament=tournament,
            team_a=team_a,
            team_b=team_b,
            defaults={
                'field': fields[match_count % len(fields)],
                'match_number': match_count + 1,
                'round_number': 1,
                'match_date': match_time.date(),
                'start_time': match_time.time(),
                'status': status,
                'team_a_score': ta_score,
                'team_b_score': tb_score
            }
        )
        
        # Update team stats for completed matches
        if is_completed:
            winner = team_a if ta_score > tb_score else team_b
            loser = team_b if winner == team_a else team_a
            winner.wins += 1
            winner.points_for += max(ta_score, tb_score)
            winner.points_against += min(ta_score, tb_score)
            loser.losses += 1
            loser.points_for += min(ta_score, tb_score)
            loser.points_against += max(ta_score, tb_score)
            winner.save()
            loser.save()
            
            # Create spirit scores
            SpiritScore.objects.get_or_create(
                match=match,
                scoring_team=team_a,
                receiving_team=team_b,
                defaults={
                    'rules_knowledge': 3,
                    'fouls_and_contact': 4,
                    'fair_mindedness': 4,
                    'positive_attitude': 3,
                    'communication': 4,
                    'is_submitted': True
                }
            )
            SpiritScore.objects.get_or_create(
                match=match,
                scoring_team=team_b,
                receiving_team=team_a,
                defaults={
                    'rules_knowledge': 4,
                    'fouls_and_contact': 3,
                    'fair_mindedness': 3,
                    'positive_attitude': 4,
                    'communication': 3,
                    'is_submitted': True
                }
            )
        
        match_count += 1

print(f'✅ Created {match_count} matches with spirit scores')

# Create announcements
announcements = [
    ('Welcome!', 'Welcome to Y-Ultimate Championship 2025!', True),
    ('Schedule Update', 'Field B matches moved 30 min later', False),
    ('Spirit Reminder', 'Submit spirit scores within 30 minutes', False),
]

for title, message, urgent in announcements:
    TournamentAnnouncement.objects.get_or_create(
        tournament=tournament,
        title=title,
        defaults={'message': message, 'is_urgent': urgent}
    )

print(f'✅ Created {len(announcements)} announcements')

print('\n' + '='*60)
print('🎉 Tournament data population complete!')
print('='*60)
print('\n📋 Login Credentials:')
print('Captains: captain1-4 / password123')
print('\n✅ Start server: python manage.py runserver')
print('✅ Admin panel: http://127.0.0.1:8000/admin/')
print('✅ Admin login: admin / admin123\n')
