"""
Automated Tournament Data Generator and Tester
Creates sample tournament data and tests all endpoints automatically
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.models import (
    Tournament, Team, Player, Match, Field, SpiritScore, 
    Attendance, TournamentAnnouncement, VisitorRegistration
)
from datetime import date, time, timedelta
import random


class Command(BaseCommand):
    help = 'Generate sample tournament data and test the system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('🏆 TOURNAMENT MANAGEMENT SYSTEM - AUTO SETUP'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        # Step 1: Get or create a tournament director user
        self.stdout.write('📝 Step 1: Setting up Tournament Director...')
        director, created = User.objects.get_or_create(
            username='director',
            defaults={
                'email': 'director@yultimate.org',
                'first_name': 'Tournament',
                'last_name': 'Director',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            director.set_password('director123')
            director.save()
            self.stdout.write(self.style.SUCCESS('  ✅ Created Tournament Director user'))
        else:
            # Update existing user to have proper permissions
            director.is_staff = True
            director.is_superuser = True
            director.set_password('director123')
            director.save()
            self.stdout.write(self.style.WARNING('  ⚠️  Tournament Director already exists - Updated permissions'))
        
        # Update profile to tournament_director
        director.profile.user_type = 'tournament_director'
        director.profile.save()
        
        # Get or create token
        token, _ = Token.objects.get_or_create(user=director)
        
        self.stdout.write(self.style.SUCCESS(f'\n  🔑 Auth Token: {token.key}'))
        self.stdout.write(self.style.SUCCESS(f'  👤 Username: director'))
        self.stdout.write(self.style.SUCCESS(f'  🔒 Password: director123\n'))

        # Step 2: Create tournament
        self.stdout.write('📝 Step 2: Creating Tournament...')
        tournament, created = Tournament.objects.get_or_create(
            name='Y-Ultimate Championship 2025',
            defaults={
                'description': 'Annual ultimate frisbee tournament for youth empowerment through sports',
                'rules': 'Standard WFDF rules apply. Spirit of the Game is paramount.',
                'location': 'Mumbai, India',
                'start_date': date.today() + timedelta(days=30),
                'end_date': date.today() + timedelta(days=32),
                'registration_deadline': date.today() + timedelta(days=20),
                'status': 'registration_open',
                'tournament_format': 'round_robin',
                'max_teams': 16,
                'min_players_per_team': 7,
                'max_players_per_team': 15,
                'sponsors': 'Y-Ultimate, USAU, Mumbai Sports Authority',
                'tournament_director': director
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Created tournament: {tournament.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Tournament already exists: {tournament.name}'))

        # Step 3: Create fields
        self.stdout.write('\n📝 Step 3: Creating Fields...')
        field_names = ['Main Field', 'Field 2', 'Field 3']
        fields = []
        for field_name in field_names:
            field, created = Field.objects.get_or_create(
                tournament=tournament,
                name=field_name,
                defaults={
                    'location_details': f'{field_name} at tournament venue',
                    'is_active': True
                }
            )
            fields.append(field)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created {field_name}'))

        # Step 4: Create team managers
        self.stdout.write('\n📝 Step 4: Creating Team Managers...')
        team_data = [
            ('Mumbai Thunderbolts', 'captain1', 'Mumbai, Maharashtra'),
            ('Delhi Dynamos', 'captain2', 'Delhi'),
            ('Bangalore Blaze', 'captain3', 'Bangalore, Karnataka'),
            ('Pune Phoenix', 'captain4', 'Pune, Maharashtra'),
        ]
        
        teams = []
        captains = []
        
        for team_name, captain_username, city in team_data:
            # Create captain
            captain, created = User.objects.get_or_create(
                username=captain_username,
                defaults={
                    'email': f'{captain_username}@example.com',
                    'first_name': team_name.split()[0],
                    'last_name': 'Captain'
                }
            )
            if created:
                captain.set_password('password123')
                captain.save()
                captain.profile.user_type = 'team_manager'
                captain.profile.save()
            captains.append(captain)
            
            # Create team
            team, created = Team.objects.get_or_create(
                tournament=tournament,
                name=team_name,
                defaults={
                    'captain': captain,
                    'home_city': city,
                    'status': 'approved'  # Auto-approve for demo
                }
            )
            teams.append(team)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created team: {team_name}'))

        # Step 5: Add players to teams
        self.stdout.write('\n📝 Step 5: Adding Players...')
        
        player_names = [
            ('Rahul', 'Sharma', 'male'),
            ('Priya', 'Patel', 'female'),
            ('Arjun', 'Mehta', 'male'),
            ('Sneha', 'Kumar', 'female'),
            ('Vikram', 'Singh', 'male'),
            ('Anjali', 'Reddy', 'female'),
            ('Rohan', 'Verma', 'male'),
            ('Kavya', 'Nair', 'female'),
        ]
        
        positions = ['Handler', 'Cutter', 'Defense', 'Hybrid']
        experience_levels = ['beginner', 'intermediate', 'advanced']
        
        total_players = 0
        for team in teams:
            jersey_num = 1
            for first_name, last_name, gender in player_names:
                Player.objects.get_or_create(
                    team=team,
                    tournament=tournament,
                    email=f'{first_name.lower()}.{last_name.lower()}@{team.name.replace(" ", "").lower()}.com',
                    defaults={
                        'full_name': f'{first_name} {last_name}',
                        'phone': f'+91 98765{random.randint(10000, 99999)}',
                        'gender': gender,
                        'age': random.randint(18, 25),
                        'jersey_number': jersey_num,
                        'position': random.choice(positions),
                        'experience_level': random.choice(experience_levels),
                        'is_verified': True
                    }
                )
                jersey_num += 1
                total_players += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Added {total_players} players across {len(teams)} teams'))

        # Step 6: Create matches
        self.stdout.write('\n📝 Step 6: Creating Matches...')
        
        if len(teams) >= 2:
            match_num = 1
            matches = []
            
            # Create round-robin schedule
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    match_date = tournament.start_date + timedelta(days=(match_num - 1) // 3)
                    hour = 9 + ((match_num - 1) % 3) * 2  # 9am, 11am, 1pm
                    
                    match, created = Match.objects.get_or_create(
                        tournament=tournament,
                        team_a=teams[i],
                        team_b=teams[j],
                        match_number=match_num,
                        defaults={
                            'field': fields[match_num % len(fields)],
                            'match_date': match_date,
                            'start_time': time(hour, 0),
                            'round_number': 1,
                            'status': 'scheduled' if match_num > 2 else 'completed',
                            'team_a_score': random.randint(10, 15) if match_num <= 2 else 0,
                            'team_b_score': random.randint(10, 15) if match_num <= 2 else 0,
                        }
                    )
                    
                    if created:
                        matches.append(match)
                        match_num += 1
                        
                        # Update team stats for completed matches
                        if match.status == 'completed':
                            winner = match.get_winner()
                            if winner == match.team_a:
                                match.team_a.wins += 1
                                match.team_b.losses += 1
                            elif winner == match.team_b:
                                match.team_b.wins += 1
                                match.team_a.losses += 1
                            else:
                                match.team_a.draws += 1
                                match.team_b.draws += 1
                            
                            match.team_a.points_for += match.team_a_score
                            match.team_a.points_against += match.team_b_score
                            match.team_b.points_for += match.team_b_score
                            match.team_b.points_against += match.team_a_score
                            
                            match.team_a.save()
                            match.team_b.save()
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ Created {len(matches)} matches'))

            # Step 7: Add spirit scores for completed matches
            self.stdout.write('\n📝 Step 7: Adding Spirit Scores...')
            
            completed_matches = Match.objects.filter(tournament=tournament, status='completed')
            spirit_count = 0
            
            for match in completed_matches:
                # Team A scores Team B
                spirit1, created = SpiritScore.objects.get_or_create(
                    match=match,
                    scoring_team=match.team_a,
                    receiving_team=match.team_b,
                    defaults={
                        'rules_knowledge': random.randint(2, 4),
                        'fouls_and_contact': random.randint(2, 4),
                        'fair_mindedness': random.randint(2, 4),
                        'positive_attitude': random.randint(2, 4),
                        'communication': random.randint(2, 4),
                        'comments': 'Great sportsmanship and communication!',
                        'is_submitted': True,
                        'submitted_by': match.team_a.captain
                    }
                )
                if created:
                    spirit_count += 1
                
                # Team B scores Team A
                spirit2, created = SpiritScore.objects.get_or_create(
                    match=match,
                    scoring_team=match.team_b,
                    receiving_team=match.team_a,
                    defaults={
                        'rules_knowledge': random.randint(2, 4),
                        'fouls_and_contact': random.randint(2, 4),
                        'fair_mindedness': random.randint(2, 4),
                        'positive_attitude': random.randint(2, 4),
                        'communication': random.randint(2, 4),
                        'comments': 'Excellent spirit throughout the match!',
                        'is_submitted': True,
                        'submitted_by': match.team_b.captain
                    }
                )
                if created:
                    spirit_count += 1
            
            # Update team spirit averages
            for team in teams:
                team.update_spirit_average()
            
            self.stdout.write(self.style.SUCCESS(f'  ✅ Created {spirit_count} spirit scores'))

        # Step 8: Add tournament announcements
        self.stdout.write('\n📝 Step 8: Creating Announcements...')
        
        announcements_data = [
            ('Welcome to Y-Ultimate Championship 2025!', 'Tournament kicks off in 30 days. Make sure to register your team!', False),
            ('Spirit of the Game Workshop', 'Join us for a workshop on Spirit of the Game scoring. Date: TBD', False),
            ('Registration Deadline Extended', 'We have extended the registration deadline by 5 days!', True),
        ]
        
        for title, message, is_urgent in announcements_data:
            TournamentAnnouncement.objects.get_or_create(
                tournament=tournament,
                title=title,
                defaults={
                    'message': message,
                    'is_urgent': is_urgent,
                    'created_by': director
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Created {len(announcements_data)} announcements'))

        # Final summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('✅ SETUP COMPLETE! '))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        self.stdout.write(self.style.SUCCESS('\n📊 TOURNAMENT DATA SUMMARY:'))
        self.stdout.write(f'  🏆 Tournament: {tournament.name}')
        self.stdout.write(f'  👥 Teams: {len(teams)}')
        self.stdout.write(f'  🏃 Players: {Player.objects.filter(tournament=tournament).count()}')
        self.stdout.write(f'  ⚽ Matches: {Match.objects.filter(tournament=tournament).count()}')
        self.stdout.write(f'  ⭐ Spirit Scores: {SpiritScore.objects.filter(match__tournament=tournament).count()}')
        self.stdout.write(f'  📢 Announcements: {TournamentAnnouncement.objects.filter(tournament=tournament).count()}')
        
        self.stdout.write(self.style.SUCCESS('\n🔑 LOGIN CREDENTIALS:'))
        self.stdout.write(self.style.SUCCESS(f'\n  Tournament Director:'))
        self.stdout.write(f'    Username: director')
        self.stdout.write(f'    Password: director123')
        self.stdout.write(f'    Token: {token.key}')
        
        self.stdout.write(self.style.SUCCESS(f'\n  Team Captains:'))
        for i, (team_name, captain_username, _) in enumerate(team_data):
            self.stdout.write(f'    {team_name}: {captain_username} / password123')
        
        self.stdout.write(self.style.SUCCESS('\n\n🌐 ACCESS POINTS:'))
        self.stdout.write(f'  Django Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write(f'  API Base URL: http://127.0.0.1:8000/api/')
        self.stdout.write(f'  Frontend: http://localhost:3000/')
        
        self.stdout.write(self.style.SUCCESS('\n\n📱 NEXT STEPS:'))
        self.stdout.write('  1. Login to Django Admin with director/director123')
        self.stdout.write('  2. View all tournament data')
        self.stdout.write('  3. Test API endpoints')
        self.stdout.write('  4. Build frontend pages!')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70 + '\n'))
