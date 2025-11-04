# api/management/commands/setup_tournament.py# api/management/commands/setup_tournament.py""""""



from django.core.management.base import BaseCommand

from django.contrib.auth.models import User

from django.utils import timezonefrom django.core.management.base import BaseCommandAutomated Tournament Data Generator and TesterAutomated Tournament Data Generator and Tester

from datetime import timedelta

from api.models import (from django.contrib.auth.models import User

    Profile, Tournament, Team, Player, Match, 

    Field, SpiritScore, TournamentAnnouncementfrom django.utils import timezoneCreates sample tournament data and tests all endpoints automaticallyCreates sample tournament data and tests all endpoints automatically

)

from rest_framework.authtoken.models import Tokenfrom datetime import timedelta



from api.models import (""""""

class Command(BaseCommand):

    help = 'Populate database with sample tournament data'    Profile, Tournament, Team, Player, Match, 



    def handle(self, *args, **kwargs):    Field, SpiritScore, TournamentAnnouncement

        self.stdout.write(self.style.SUCCESS('Starting tournament data setup...'))

        )

        # Create tournament director user

        director_user, created = User.objects.get_or_create(from rest_framework.authtoken.models import Tokenfrom django.core.management.base import BaseCommandfrom django.core.management.base import BaseCommand

            username='director',

            defaults={

                'email': 'director@yultimate.com',

                'first_name': 'Tournament',from django.contrib.auth.models import Userfrom django.contrib.auth.models import User

                'last_name': 'Director'

            }class Command(BaseCommand):

        )

        if created:    help = 'Populate database with sample tournament data'from rest_framework.authtoken.models import Tokenfrom rest_framework.authtoken.models import Token

            director_user.set_password('director123')

            director_user.save()

            Token.objects.create(user=director_user)

            self.stdout.write(self.style.SUCCESS(f'✅ Created director user'))    def handle(self, *args, **kwargs):from api.models import (from api.models import (

        

        # Create director profile        self.stdout.write(self.style.SUCCESS('Starting tournament data setup...'))

        director_profile, _ = Profile.objects.get_or_create(

            user=director_user,            Tournament, Team, Player, Match, Field, SpiritScore,    Tournament, Team, Player, Match, Field, SpiritScore, 

            defaults={

                'first_name': 'Tournament',        # Create tournament director user

                'last_name': 'Director',

                'email': 'director@yultimate.com',        director_user, created = User.objects.get_or_create(    Attendance, TournamentAnnouncement, VisitorRegistration, Profile    Attendance, TournamentAnnouncement, VisitorRegistration

                'user_type': 'tournament_director',

                'role': 'tournament_director',            username='director',

                'phone': '+91-9876543210',

                'age': 35,            defaults={))

                'profile_completed': True

            }                'email': 'director@yultimate.com',

        )

                        'first_name': 'Tournament',from datetime import date, time, timedeltafrom datetime import date, time, timedelta

        # Create tournament

        tournament, created = Tournament.objects.get_or_create(                'last_name': 'Director'

            name='Y-Ultimate Championship 2025',

            defaults={            }import randomimport random

                'description': 'The premier Ultimate Frisbee tournament featuring top teams from across India. Experience the spirit of the game!',

                'location': 'Jawaharlal Nehru Stadium, Delhi',        )

                'start_date': timezone.now().date(),

                'end_date': (timezone.now() + timedelta(days=3)).date(),        if created:

                'registration_deadline': (timezone.now() - timedelta(days=7)).date(),

                'status': 'ongoing',            director_user.set_password('director123')

                'tournament_format': 'round_robin',

                'max_teams': 8,            director_user.save()

                'rules': 'Standard WFDF rules apply. Spirit of the Game is paramount.',

                'sponsors': 'Nike, Adidas, Red Bull'            Token.objects.create(user=director_user)

            }

        )            self.stdout.write(self.style.SUCCESS(f'✅ Created director user'))class Command(BaseCommand):class Command(BaseCommand):

        if created:

            self.stdout.write(self.style.SUCCESS(f'✅ Created tournament: {tournament.name}'))        

        

        # Create fields        # Create director profile    help = 'Generate sample tournament data and test the system'    help = 'Generate sample tournament data and test the system'

        fields_data = [

            {'name': 'Field A', 'location': 'North Zone'},        director_profile, _ = Profile.objects.get_or_create(

            {'name': 'Field B', 'location': 'South Zone'},

            {'name': 'Field C', 'location': 'East Zone'},            user=director_user,

        ]

                    defaults={

        fields = []

        for field_data in fields_data:                'first_name': 'Tournament',    def handle(self, *args, **kwargs):    def handle(self, *args, **kwargs):

            field, created = Field.objects.get_or_create(

                tournament=tournament,                'last_name': 'Director',

                name=field_data['name'],

                defaults={'location': field_data['location']}                'email': 'director@yultimate.com',        self.stdout.write(self.style.SUCCESS('\n' + '='*70))        self.stdout.write(self.style.SUCCESS('\n' + '='*70))

            )

            fields.append(field)                'user_type': 'tournament_director',

            if created:

                self.stdout.write(self.style.SUCCESS(f'✅ Created field: {field.name}'))                'role': 'tournament_director',        self.stdout.write(self.style.SUCCESS('🏆 TOURNAMENT MANAGEMENT SYSTEM - AUTO SETUP'))        self.stdout.write(self.style.SUCCESS('🏆 TOURNAMENT MANAGEMENT SYSTEM - AUTO SETUP'))

        

        # Create teams with captains                'phone': '+91-9876543210',

        teams_data = [

            {                'age': 35,        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

                'name': 'Mumbai Thunderbolts',

                'city': 'Mumbai',                'profile_completed': True

                'captain': {'username': 'captain1', 'first': 'Raj', 'last': 'Sharma'},

                'color': '#FF6B35'            }

            },

            {        )

                'name': 'Delhi Dynamos',

                'city': 'Delhi',                # Step 1: Get or create a tournament director user        # Step 1: Get or create a tournament director user

                'captain': {'username': 'captain2', 'first': 'Priya', 'last': 'Singh'},

                'color': '#004E89'        # Create tournament

            },

            {        tournament, created = Tournament.objects.get_or_create(        self.stdout.write('📝 Step 1: Setting up Tournament Director...')        self.stdout.write('📝 Step 1: Setting up Tournament Director...')

                'name': 'Bangalore Blaze',

                'city': 'Bangalore',            name='Y-Ultimate Championship 2025',

                'captain': {'username': 'captain3', 'first': 'Arjun', 'last': 'Patel'},

                'color': '#F77F00'            defaults={        director, created = User.objects.get_or_create(        director, created = User.objects.get_or_create(

            },

            {                'description': 'The premier Ultimate Frisbee tournament featuring top teams from across India. Experience the spirit of the game!',

                'name': 'Pune Phoenix',

                'city': 'Pune',                'location': 'Jawaharlal Nehru Stadium, Delhi',            username='director',            username='director',

                'captain': {'username': 'captain4', 'first': 'Neha', 'last': 'Gupta'},

                'color': '#06A77D'                'start_date': timezone.now().date(),

            },

        ]                'end_date': (timezone.now() + timedelta(days=3)).date(),            defaults={            defaults={

        

        teams = []                'registration_deadline': (timezone.now() - timedelta(days=7)).date(),

        for idx, team_data in enumerate(teams_data):

            # Create captain user                'status': 'ongoing',                'email': 'director@yultimate.org',                'email': 'director@yultimate.org',

            captain_user, created = User.objects.get_or_create(

                username=team_data['captain']['username'],                'tournament_format': 'round_robin',

                defaults={

                    'email': f"{team_data['captain']['username']}@yultimate.com",                'max_teams': 8,                'first_name': 'Tournament',                'first_name': 'Tournament',

                    'first_name': team_data['captain']['first'],

                    'last_name': team_data['captain']['last']                'rules': 'Standard WFDF rules apply. Spirit of the Game is paramount.',

                }

            )                'sponsors': 'Nike, Adidas, Red Bull'                'last_name': 'Director',                'last_name': 'Director',

            if created:

                captain_user.set_password('password123')            }

                captain_user.save()

                Token.objects.create(user=captain_user)        )                'is_staff': True,                'is_staff': True,

            

            # Create captain profile        if created:

            Profile.objects.get_or_create(

                user=captain_user,            self.stdout.write(self.style.SUCCESS(f'✅ Created tournament: {tournament.name}'))                'is_superuser': True                'is_superuser': True

                defaults={

                    'first_name': team_data['captain']['first'],        

                    'last_name': team_data['captain']['last'],

                    'email': f"{team_data['captain']['username']}@yultimate.com",        # Create fields            }            }

                    'user_type': 'coach',

                    'role': 'captain',        fields_data = [

                    'team_name': team_data['name'],

                    'phone': f'+91-98765432{idx}0',            {'name': 'Field A', 'location': 'North Zone'},        )        )

                    'age': 25,

                    'school': f"{team_data['city']} Sports Academy",            {'name': 'Field B', 'location': 'South Zone'},

                    'profile_completed': True

                }            {'name': 'Field C', 'location': 'East Zone'},        if created:        if created:

            )

                    ]

            # Create team

            team, created = Team.objects.get_or_create(                    director.set_password('director123')            director.set_password('director123')

                tournament=tournament,

                name=team_data['name'],        fields = []

                defaults={

                    'captain': captain_user,        for field_data in fields_data:            director.save()            director.save()

                    'home_city': team_data['city'],

                    'status': 'registered',            field, created = Field.objects.get_or_create(

                    'wins': 0,

                    'losses': 0,                tournament=tournament,            self.stdout.write(self.style.SUCCESS('  ✅ Created Tournament Director user'))            self.stdout.write(self.style.SUCCESS('  ✅ Created Tournament Director user'))

                    'draws': 0,

                    'points': 0                name=field_data['name'],

                }

            )                defaults={'location': field_data['location']}        else:        else:

            teams.append(team)

            if created:            )

                self.stdout.write(self.style.SUCCESS(f'✅ Created team: {team.name}'))

                        fields.append(field)            # Update existing user to have proper permissions            # Update existing user to have proper permissions

            # Create 8 players per team

            positions = ['Handler', 'Cutter', 'Hybrid', 'Deep', 'Handler', 'Cutter', 'Hybrid', 'Deep']            if created:

            first_names = ['Amit', 'Sneha', 'Vikram', 'Pooja', 'Rahul', 'Anjali', 'Karan', 'Meera']

            last_names = ['Kumar', 'Reddy', 'Iyer', 'Joshi', 'Verma', 'Nair', 'Chopra', 'Desai']                self.stdout.write(self.style.SUCCESS(f'✅ Created field: {field.name}'))            director.is_staff = True            director.is_staff = True

            

            for i in range(8):        

                player, created = Player.objects.get_or_create(

                    team=team,        # Create teams with captains            director.is_superuser = True            director.is_superuser = True

                    jersey_number=i + 1,

                    defaults={        teams_data = [

                        'tournament': tournament,

                        'full_name': f"{first_names[i]} {last_names[i]}",            {            director.set_password('director123')            director.set_password('director123')

                        'email': f"{first_names[i].lower()}.{last_names[i].lower()}@yultimate.com",

                        'phone': f'+91-987654{i:04d}',                'name': 'Mumbai Thunderbolts',

                        'gender': 'Male' if i % 2 == 0 else 'Female',

                        'age': 20 + i,                'city': 'Mumbai',            director.save()            director.save()

                        'position': positions[i],

                        'experience_level': 'Intermediate' if i < 4 else 'Advanced',                'captain': {'username': 'captain1', 'first': 'Raj', 'last': 'Sharma'},

                        'is_active': True

                    }                'color': '#FF6B35'            self.stdout.write(self.style.WARNING('  ⚠️  Tournament Director already exists - Updated permissions'))            self.stdout.write(self.style.WARNING('  ⚠️  Tournament Director already exists - Updated permissions'))

                )

                if created:            },

                    # Create user for player

                    player_username = f"{first_names[i].lower()}_{team_data['name'].split()[0].lower()}"            {                

                    player_user, user_created = User.objects.get_or_create(

                        username=player_username,                'name': 'Delhi Dynamos',

                        defaults={

                            'email': f"{first_names[i].lower()}.{last_names[i].lower()}@yultimate.com",                'city': 'Delhi',        # Update profile to tournament_director        # Update profile to tournament_director

                            'first_name': first_names[i],

                            'last_name': last_names[i]                'captain': {'username': 'captain2', 'first': 'Priya', 'last': 'Singh'},

                        }

                    )                'color': '#004E89'        profile, _ = Profile.objects.get_or_create(user=director)        director.profile.user_type = 'tournament_director'

                    if user_created:

                        player_user.set_password('player123')            },

                        player_user.save()

                        Token.objects.create(user=player_user)            {        profile.user_type = 'tournament_director'        director.profile.save()

                    

                    # Create player profile                'name': 'Bangalore Blaze',

                    Profile.objects.get_or_create(

                        user=player_user,                'city': 'Bangalore',        profile.role = 'tournament_director'        

                        defaults={

                            'first_name': first_names[i],                'captain': {'username': 'captain3', 'first': 'Arjun', 'last': 'Patel'},

                            'last_name': last_names[i],

                            'email': f"{first_names[i].lower()}.{last_names[i].lower()}@yultimate.com",                'color': '#F77F00'        profile.save()        # Get or create token

                            'user_type': 'student',

                            'role': 'player',            },

                            'team_name': team.name,

                            'phone': f'+91-987654{i:04d}',            {                token, _ = Token.objects.get_or_create(user=director)

                            'age': 20 + i,

                            'school': f"{team_data['city']} Sports Academy",                'name': 'Pune Phoenix',

                            'profile_completed': True

                        }                'city': 'Pune',        # Get or create token        

                    )

                        'captain': {'username': 'captain4', 'first': 'Neha', 'last': 'Gupta'},

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(teams)} teams with 8 players each'))

                        'color': '#06A77D'        token, _ = Token.objects.get_or_create(user=director)        self.stdout.write(self.style.SUCCESS(f'\n  🔑 Auth Token: {token.key}'))

        # Create matches

        match_counter = 0            },

        for i, team1 in enumerate(teams):

            for team2 in teams[i+1:]:        ]                self.stdout.write(self.style.SUCCESS(f'  👤 Username: director'))

                match_time = timezone.now() + timedelta(hours=match_counter * 2)

                        

                # Determine match status and scores

                if match_counter < 3:  # First 3 matches completed        teams = []        self.stdout.write(self.style.SUCCESS(f'\n  🔑 Auth Token: {token.key}'))        self.stdout.write(self.style.SUCCESS(f'  🔒 Password: director123\n'))

                    status = 'completed'

                    team1_score = 13 if match_counter % 2 == 0 else 10        for team_data in teams_data:

                    team2_score = 10 if match_counter % 2 == 0 else 13

                    winner = team1 if team1_score > team2_score else team2            # Create captain user        self.stdout.write(self.style.SUCCESS(f'  👤 Username: director'))

                    

                    # Update team stats            captain_user, created = User.objects.get_or_create(

                    if winner == team1:

                        team1.wins += 1                username=team_data['captain']['username'],        self.stdout.write(self.style.SUCCESS(f'  🔒 Password: director123\n'))        # Step 2: Create tournament

                        team1.points += 3

                        team2.losses += 1                defaults={

                    else:

                        team2.wins += 1                    'email': f"{team_data['captain']['username']}@yultimate.com",        self.stdout.write('📝 Step 2: Creating Tournament...')

                        team2.points += 3

                        team1.losses += 1                    'first_name': team_data['captain']['first'],

                    

                    team1.points_for += team1_score                    'last_name': team_data['captain']['last']        # Step 2: Create tournament        tournament, created = Tournament.objects.get_or_create(

                    team1.points_against += team2_score

                    team2.points_for += team2_score                }

                    team2.points_against += team1_score

                    team1.save()            )        self.stdout.write('📝 Step 2: Creating Tournament...')            name='Y-Ultimate Championship 2025',

                    team2.save()

                                if created:

                elif match_counter == 3:  # One match in progress

                    status = 'in_progress'                captain_user.set_password('password123')        tournament, created = Tournament.objects.get_or_create(            defaults={

                    team1_score = 7

                    team2_score = 5                captain_user.save()

                else:  # Rest scheduled

                    status = 'scheduled'                Token.objects.create(user=captain_user)            name='Y-Ultimate Championship 2025',                'description': 'Annual ultimate frisbee tournament for youth empowerment through sports',

                    team1_score = 0

                    team2_score = 0            

                

                match, created = Match.objects.get_or_create(            # Create captain profile            defaults={                'rules': 'Standard WFDF rules apply. Spirit of the Game is paramount.',

                    tournament=tournament,

                    team1=team1,            Profile.objects.get_or_create(

                    team2=team2,

                    defaults={                user=captain_user,                'description': 'Annual ultimate frisbee tournament for youth empowerment through sports',                'location': 'Mumbai, India',

                        'field': fields[match_counter % len(fields)],

                        'scheduled_time': match_time,                defaults={

                        'status': status,

                        'team1_score': team1_score,                    'first_name': team_data['captain']['first'],                'rules': 'Standard WFDF rules apply. Spirit of the Game is paramount.',                'start_date': date.today() + timedelta(days=30),

                        'team2_score': team2_score

                    }                    'last_name': team_data['captain']['last'],

                )

                                    'email': f"{team_data['captain']['username']}@yultimate.com",                'location': 'Mumbai, India',                'end_date': date.today() + timedelta(days=32),

                # Create spirit scores for completed matches

                if status == 'completed':                    'user_type': 'coach',

                    # Team1 scores Team2

                    SpiritScore.objects.get_or_create(                    'role': 'captain',                'start_date': date.today() + timedelta(days=30),                'registration_deadline': date.today() + timedelta(days=20),

                        match=match,

                        tournament=tournament,                    'team_name': team_data['name'],

                        scoring_team=team1,

                        receiving_team=team2,                    'phone': f'+91-98765432{len(teams)}',                'end_date': date.today() + timedelta(days=32),                'status': 'registration_open',

                        defaults={

                            'rules_knowledge': 3,                    'age': 25,

                            'fouls_and_contact': 3,

                            'fair_mindedness': 4,                    'school': f"{team_data['city']} Sports Academy",                'registration_deadline': date.today() + timedelta(days=20),                'tournament_format': 'round_robin',

                            'positive_attitude': 4,

                            'communication': 3,                    'profile_completed': True

                            'comments': 'Great sportsmanship!',

                            'is_submitted': True,                }                'status': 'registration_open',                'max_teams': 16,

                            'submitted_by': team1.captain

                        }            )

                    )

                                                'tournament_format': 'round_robin',                'min_players_per_team': 7,

                    # Team2 scores Team1

                    SpiritScore.objects.get_or_create(            # Create team

                        match=match,

                        tournament=tournament,            team, created = Team.objects.get_or_create(                'max_teams': 16,                'max_players_per_team': 15,

                        scoring_team=team2,

                        receiving_team=team1,                tournament=tournament,

                        defaults={

                            'rules_knowledge': 4,                name=team_data['name'],                'min_players_per_team': 7,                'sponsors': 'Y-Ultimate, USAU, Mumbai Sports Authority',

                            'fouls_and_contact': 3,

                            'fair_mindedness': 3,                defaults={

                            'positive_attitude': 4,

                            'communication': 4,                    'captain': captain_user,                'max_players_per_team': 15,                'tournament_director': director

                            'comments': 'Excellent teamwork and spirit!',

                            'is_submitted': True,                    'home_city': team_data['city'],

                            'submitted_by': team2.captain

                        }                    'status': 'registered',                'sponsors': 'Y-Ultimate, USAU, Mumbai Sports Authority',            }

                    )

                                    'wins': 0,

                if created:

                    match_counter += 1                    'losses': 0,                'tournament_director': director        )

        

        self.stdout.write(self.style.SUCCESS(f'✅ Created {match_counter} matches'))                    'draws': 0,

        

        # Create announcements                    'points': 0            }        

        announcements_data = [

            {                }

                'title': 'Welcome to Y-Ultimate Championship 2025!',

                'content': 'We are excited to have you all here. Remember, Spirit of the Game is our core value. Play hard, play fair!',            )        )        if created:

                'priority': 'high'

            },            teams.append(team)

            {

                'title': 'Schedule Update',            if created:                    self.stdout.write(self.style.SUCCESS(f'  ✅ Created tournament: {tournament.name}'))

                'content': 'All matches on Field B have been moved 30 minutes later due to field maintenance. Please check the updated schedule.',

                'priority': 'medium'                self.stdout.write(self.style.SUCCESS(f'✅ Created team: {team.name}'))

            },

            {                    if created:        else:

                'title': 'Spirit Score Submission Reminder',

                'content': 'Please submit your spirit scores within 30 minutes after each match. Captains are responsible for submission.',            # Create 8 players per team

                'priority': 'normal'

            },            positions = ['Handler', 'Cutter', 'Hybrid', 'Deep', 'Handler', 'Cutter', 'Hybrid', 'Deep']            self.stdout.write(self.style.SUCCESS(f'  ✅ Created tournament: {tournament.name}'))            self.stdout.write(self.style.WARNING(f'  ⚠️  Tournament already exists: {tournament.name}'))

        ]

                    first_names = ['Amit', 'Sneha', 'Vikram', 'Pooja', 'Rahul', 'Anjali', 'Karan', 'Meera']

        for ann_data in announcements_data:

            TournamentAnnouncement.objects.get_or_create(            last_names = ['Kumar', 'Reddy', 'Iyer', 'Joshi', 'Verma', 'Nair', 'Chopra', 'Desai']        else:

                tournament=tournament,

                title=ann_data['title'],            

                defaults={

                    'content': ann_data['content'],            for i in range(8):            self.stdout.write(self.style.WARNING(f'  ⚠️  Tournament already exists: {tournament.name}'))        # Step 3: Create fields

                    'priority': ann_data['priority']

                }                player, created = Player.objects.get_or_create(

            )

                            team=team,        self.stdout.write('\n📝 Step 3: Creating Fields...')

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(announcements_data)} announcements'))

                            jersey_number=i + 1,

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))

        self.stdout.write(self.style.SUCCESS('🎉 Tournament data setup complete!'))                    defaults={        # Step 3: Create fields        field_names = ['Main Field', 'Field 2', 'Field 3']

        self.stdout.write(self.style.SUCCESS('='*50))

        self.stdout.write(self.style.WARNING('\n📋 Login Credentials:'))                        'tournament': tournament,

        self.stdout.write(self.style.WARNING('Director: director / director123'))

        self.stdout.write(self.style.WARNING('Captains: captain1-4 / password123'))                        'full_name': f"{first_names[i]} {last_names[i]}",        self.stdout.write('\n📝 Step 3: Creating Fields...')        fields = []

        self.stdout.write(self.style.WARNING('Players: amit_mumbai, sneha_delhi, etc. / player123'))

        self.stdout.write(self.style.SUCCESS('\n✅ Access admin panel: http://127.0.0.1:8000/admin/'))                        'email': f"{first_names[i].lower()}.{last_names[i].lower()}@yultimate.com",

        self.stdout.write(self.style.SUCCESS('✅ Admin login: admin / admin123\n'))

                        'phone': f'+91-98765{i:05d}',        field_names = ['Main Field', 'Field 2', 'Field 3']        for field_name in field_names:

                        'gender': 'Male' if i % 2 == 0 else 'Female',

                        'age': 20 + i,        fields = []            field, created = Field.objects.get_or_create(

                        'position': positions[i],

                        'experience_level': 'Intermediate' if i < 4 else 'Advanced',        for field_name in field_names:                tournament=tournament,

                        'is_active': True

                    }            field, created = Field.objects.get_or_create(                name=field_name,

                )

                if created:                tournament=tournament,                defaults={

                    # Create user for player

                    player_username = f"{first_names[i].lower()}_{team_data['name'].split()[0].lower()}"                name=field_name,                    'location_details': f'{field_name} at tournament venue',

                    player_user, user_created = User.objects.get_or_create(

                        username=player_username,                defaults={                    'is_active': True

                        defaults={

                            'email': f"{first_names[i].lower()}.{last_names[i].lower()}@yultimate.com",                    'location_details': f'{field_name} at tournament venue',                }

                            'first_name': first_names[i],

                            'last_name': last_names[i]                    'is_active': True            )

                        }

                    )                }            fields.append(field)

                    if user_created:

                        player_user.set_password('player123')            )            if created:

                        player_user.save()

                        Token.objects.create(user=player_user)            fields.append(field)                self.stdout.write(self.style.SUCCESS(f'  ✅ Created {field_name}'))

                    

                    # Create player profile            if created:

                    Profile.objects.get_or_create(

                        user=player_user,                self.stdout.write(self.style.SUCCESS(f'  ✅ Created {field_name}'))        # Step 4: Create team managers

                        defaults={

                            'first_name': first_names[i],        self.stdout.write('\n📝 Step 4: Creating Team Managers...')

                            'last_name': last_names[i],

                            'email': f"{first_names[i].lower()}.{last_names[i].lower()}@yultimate.com",        # Step 4: Create team managers        team_data = [

                            'user_type': 'student',

                            'role': 'player',        self.stdout.write('\n📝 Step 4: Creating Team Managers...')            ('Mumbai Thunderbolts', 'captain1', 'Mumbai, Maharashtra'),

                            'team_name': team.name,

                            'phone': f'+91-98765{i:05d}',        team_data = [            ('Delhi Dynamos', 'captain2', 'Delhi'),

                            'age': 20 + i,

                            'school': f"{team_data['city']} Sports Academy",            ('Mumbai Thunderbolts', 'captain1', 'Mumbai, Maharashtra'),            ('Bangalore Blaze', 'captain3', 'Bangalore, Karnataka'),

                            'profile_completed': True

                        }            ('Delhi Dynamos', 'captain2', 'Delhi'),            ('Pune Phoenix', 'captain4', 'Pune, Maharashtra'),

                    )

                    ('Bangalore Blaze', 'captain3', 'Bangalore, Karnataka'),        ]

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(teams)} teams with 8 players each'))

                    ('Pune Phoenix', 'captain4', 'Pune, Maharashtra'),        

        # Create matches

        match_counter = 0        ]        teams = []

        for i, team1 in enumerate(teams):

            for team2 in teams[i+1:]:                captains = []

                match_time = timezone.now() + timedelta(hours=match_counter * 2)

                        teams = []        

                # Determine match status and scores

                if match_counter < 3:  # First 3 matches completed        captains = []        for team_name, captain_username, city in team_data:

                    status = 'completed'

                    team1_score = 13 if match_counter % 2 == 0 else 10                    # Create captain

                    team2_score = 10 if match_counter % 2 == 0 else 13

                    winner = team1 if team1_score > team2_score else team2        for team_name, captain_username, city in team_data:            captain, created = User.objects.get_or_create(

                    

                    # Update team stats            # Create captain                username=captain_username,

                    if winner == team1:

                        team1.wins += 1            captain, created = User.objects.get_or_create(                defaults={

                        team1.points += 3

                        team2.losses += 1                username=captain_username,                    'email': f'{captain_username}@example.com',

                    else:

                        team2.wins += 1                defaults={                    'first_name': team_name.split()[0],

                        team2.points += 3

                        team1.losses += 1                    'email': f'{captain_username}@example.com',                    'last_name': 'Captain'

                    

                    team1.points_for += team1_score                    'first_name': team_name.split()[0],                }

                    team1.points_against += team2_score

                    team2.points_for += team2_score                    'last_name': 'Captain'            )

                    team2.points_against += team1_score

                    team1.save()                }            if created:

                    team2.save()

                                )                captain.set_password('password123')

                elif match_counter == 3:  # One match in progress

                    status = 'in_progress'            if created:                captain.save()

                    team1_score = 7

                    team2_score = 5                captain.set_password('password123')                captain.profile.user_type = 'team_manager'

                else:  # Rest scheduled

                    status = 'scheduled'                captain.save()                captain.profile.save()

                    team1_score = 0

                    team2_score = 0                        captains.append(captain)

                

                match, created = Match.objects.get_or_create(            profile, _ = Profile.objects.get_or_create(user=captain)            

                    tournament=tournament,

                    team1=team1,            profile.user_type = 'coach'            # Create team

                    team2=team2,

                    defaults={            profile.role = 'captain'            team, created = Team.objects.get_or_create(

                        'field': fields[match_counter % len(fields)],

                        'scheduled_time': match_time,            profile.save()                tournament=tournament,

                        'status': status,

                        'team1_score': team1_score,                            name=team_name,

                        'team2_score': team2_score

                    }            captains.append(captain)                defaults={

                )

                                                'captain': captain,

                # Create spirit scores for completed matches

                if status == 'completed':            # Create team                    'home_city': city,

                    # Team1 scores Team2

                    SpiritScore.objects.get_or_create(            team, created = Team.objects.get_or_create(                    'status': 'approved'  # Auto-approve for demo

                        match=match,

                        tournament=tournament,                tournament=tournament,                }

                        scoring_team=team1,

                        receiving_team=team2,                name=team_name,            )

                        defaults={

                            'rules_knowledge': 3,                defaults={            teams.append(team)

                            'fouls_and_contact': 3,

                            'fair_mindedness': 4,                    'captain': captain,            

                            'positive_attitude': 4,

                            'communication': 3,                    'home_city': city,            if created:

                            'comments': 'Great sportsmanship!',

                            'is_submitted': True,                    'status': 'approved'  # Auto-approve for demo                self.stdout.write(self.style.SUCCESS(f'  ✅ Created team: {team_name}'))

                            'submitted_by': team1.captain

                        }                }

                    )

                                )        # Step 5: Add players to teams

                    # Team2 scores Team1

                    SpiritScore.objects.get_or_create(            teams.append(team)        self.stdout.write('\n📝 Step 5: Adding Players...')

                        match=match,

                        tournament=tournament,                    

                        scoring_team=team2,

                        receiving_team=team1,            if created:        player_names = [

                        defaults={

                            'rules_knowledge': 4,                self.stdout.write(self.style.SUCCESS(f'  ✅ Created team: {team_name}'))            ('Rahul', 'Sharma', 'male'),

                            'fouls_and_contact': 3,

                            'fair_mindedness': 3,            ('Priya', 'Patel', 'female'),

                            'positive_attitude': 4,

                            'communication': 4,        # Step 5: Add players to teams            ('Arjun', 'Mehta', 'male'),

                            'comments': 'Excellent teamwork and spirit!',

                            'is_submitted': True,        self.stdout.write('\n📝 Step 5: Adding Players...')            ('Sneha', 'Kumar', 'female'),

                            'submitted_by': team2.captain

                        }                    ('Vikram', 'Singh', 'male'),

                    )

                        player_names = [            ('Anjali', 'Reddy', 'female'),

                if created:

                    match_counter += 1            ('Rahul', 'Sharma', 'male'),            ('Rohan', 'Verma', 'male'),

        

        self.stdout.write(self.style.SUCCESS(f'✅ Created {match_counter} matches'))            ('Priya', 'Patel', 'female'),            ('Kavya', 'Nair', 'female'),

        

        # Create announcements            ('Arjun', 'Mehta', 'male'),        ]

        announcements_data = [

            {            ('Sneha', 'Kumar', 'female'),        

                'title': 'Welcome to Y-Ultimate Championship 2025!',

                'content': 'We are excited to have you all here. Remember, Spirit of the Game is our core value. Play hard, play fair!',            ('Vikram', 'Singh', 'male'),        positions = ['Handler', 'Cutter', 'Defense', 'Hybrid']

                'priority': 'high'

            },            ('Anjali', 'Reddy', 'female'),        experience_levels = ['beginner', 'intermediate', 'advanced']

            {

                'title': 'Schedule Update',            ('Rohan', 'Verma', 'male'),        

                'content': 'All matches on Field B have been moved 30 minutes later due to field maintenance. Please check the updated schedule.',

                'priority': 'medium'            ('Kavya', 'Nair', 'female'),        total_players = 0

            },

            {        ]        for team in teams:

                'title': 'Spirit Score Submission Reminder',

                'content': 'Please submit your spirit scores within 30 minutes after each match. Captains are responsible for submission.',                    jersey_num = 1

                'priority': 'normal'

            },        positions = ['Handler', 'Cutter', 'Defense', 'Hybrid']            for first_name, last_name, gender in player_names:

        ]

                experience_levels = ['beginner', 'intermediate', 'advanced']                Player.objects.get_or_create(

        for ann_data in announcements_data:

            TournamentAnnouncement.objects.get_or_create(                            team=team,

                tournament=tournament,

                title=ann_data['title'],        total_players = 0                    tournament=tournament,

                defaults={

                    'content': ann_data['content'],        for team in teams:                    email=f'{first_name.lower()}.{last_name.lower()}@{team.name.replace(" ", "").lower()}.com',

                    'priority': ann_data['priority']

                }            jersey_num = 1                    defaults={

            )

                    for first_name, last_name, gender in player_names:                        'full_name': f'{first_name} {last_name}',

        self.stdout.write(self.style.SUCCESS(f'✅ Created {len(announcements_data)} announcements'))

                        Player.objects.get_or_create(                        'phone': f'+91 98765{random.randint(10000, 99999)}',

        self.stdout.write(self.style.SUCCESS('\n' + '='*50))

        self.stdout.write(self.style.SUCCESS('🎉 Tournament data setup complete!'))                    team=team,                        'gender': gender,

        self.stdout.write(self.style.SUCCESS('='*50))

        self.stdout.write(self.style.WARNING('\n📋 Login Credentials:'))                    tournament=tournament,                        'age': random.randint(18, 25),

        self.stdout.write(self.style.WARNING('Director: director / director123'))

        self.stdout.write(self.style.WARNING('Captains: captain1-4 / password123'))                    email=f'{first_name.lower()}.{last_name.lower()}@{team.name.replace(" ", "").lower()}.com',                        'jersey_number': jersey_num,

        self.stdout.write(self.style.WARNING('Players: amit_mumbai, sneha_delhi, etc. / player123'))

        self.stdout.write(self.style.SUCCESS('\n✅ Access admin panel: http://127.0.0.1:8000/admin/'))                    defaults={                        'position': random.choice(positions),

        self.stdout.write(self.style.SUCCESS('✅ Admin login: admin / admin123\n'))

                        'full_name': f'{first_name} {last_name}',                        'experience_level': random.choice(experience_levels),

                        'phone': f'+91 98765{random.randint(10000, 99999)}',                        'is_verified': True

                        'gender': gender,                    }

                        'age': random.randint(18, 25),                )

                        'jersey_number': jersey_num,                jersey_num += 1

                        'position': random.choice(positions),                total_players += 1

                        'experience_level': random.choice(experience_levels),        

                        'is_verified': True        self.stdout.write(self.style.SUCCESS(f'  ✅ Added {total_players} players across {len(teams)} teams'))

                    }

                )        # Step 6: Create matches

                jersey_num += 1        self.stdout.write('\n📝 Step 6: Creating Matches...')

                total_players += 1        

                if len(teams) >= 2:

        self.stdout.write(self.style.SUCCESS(f'  ✅ Added {total_players} players across {len(teams)} teams'))            match_num = 1

            matches = []

        # Step 6: Create matches            

        self.stdout.write('\n📝 Step 6: Creating Matches...')            # Create round-robin schedule

                    for i in range(len(teams)):

        if len(teams) >= 2:                for j in range(i + 1, len(teams)):

            match_num = 1                    match_date = tournament.start_date + timedelta(days=(match_num - 1) // 3)

            matches = []                    hour = 9 + ((match_num - 1) % 3) * 2  # 9am, 11am, 1pm

                                

            # Create round-robin schedule                    match, created = Match.objects.get_or_create(

            for i in range(len(teams)):                        tournament=tournament,

                for j in range(i + 1, len(teams)):                        team_a=teams[i],

                    match_date = tournament.start_date + timedelta(days=(match_num - 1) // 3)                        team_b=teams[j],

                    hour = 9 + ((match_num - 1) % 3) * 2  # 9am, 11am, 1pm                        match_number=match_num,

                                            defaults={

                    match, created = Match.objects.get_or_create(                            'field': fields[match_num % len(fields)],

                        tournament=tournament,                            'match_date': match_date,

                        team_a=teams[i],                            'start_time': time(hour, 0),

                        team_b=teams[j],                            'round_number': 1,

                        match_number=match_num,                            'status': 'scheduled' if match_num > 2 else 'completed',

                        defaults={                            'team_a_score': random.randint(10, 15) if match_num <= 2 else 0,

                            'field': fields[match_num % len(fields)],                            'team_b_score': random.randint(10, 15) if match_num <= 2 else 0,

                            'match_date': match_date,                        }

                            'start_time': time(hour, 0),                    )

                            'round_number': 1,                    

                            'status': 'scheduled' if match_num > 2 else 'completed',                    if created:

                            'team_a_score': random.randint(10, 15) if match_num <= 2 else 0,                        matches.append(match)

                            'team_b_score': random.randint(10, 15) if match_num <= 2 else 0,                        match_num += 1

                        }                        

                    )                        # Update team stats for completed matches

                                            if match.status == 'completed':

                    if created:                            winner = match.get_winner()

                        matches.append(match)                            if winner == match.team_a:

                        match_num += 1                                match.team_a.wins += 1

                                                        match.team_b.losses += 1

                        # Update team stats for completed matches                            elif winner == match.team_b:

                        if match.status == 'completed':                                match.team_b.wins += 1

                            winner = match.get_winner()                                match.team_a.losses += 1

                            if winner == match.team_a:                            else:

                                match.team_a.wins += 1                                match.team_a.draws += 1

                                match.team_b.losses += 1                                match.team_b.draws += 1

                            elif winner == match.team_b:                            

                                match.team_b.wins += 1                            match.team_a.points_for += match.team_a_score

                                match.team_a.losses += 1                            match.team_a.points_against += match.team_b_score

                            else:                            match.team_b.points_for += match.team_b_score

                                match.team_a.draws += 1                            match.team_b.points_against += match.team_a_score

                                match.team_b.draws += 1                            

                                                        match.team_a.save()

                            match.team_a.points_for += match.team_a_score                            match.team_b.save()

                            match.team_a.points_against += match.team_b_score            

                            match.team_b.points_for += match.team_b_score            self.stdout.write(self.style.SUCCESS(f'  ✅ Created {len(matches)} matches'))

                            match.team_b.points_against += match.team_a_score

                                        # Step 7: Add spirit scores for completed matches

                            match.team_a.save()            self.stdout.write('\n📝 Step 7: Adding Spirit Scores...')

                            match.team_b.save()            

                        completed_matches = Match.objects.filter(tournament=tournament, status='completed')

            self.stdout.write(self.style.SUCCESS(f'  ✅ Created {len(matches)} matches'))            spirit_count = 0

            

            # Step 7: Add spirit scores for completed matches            for match in completed_matches:

            self.stdout.write('\n📝 Step 7: Adding Spirit Scores...')                # Team A scores Team B

                            spirit1, created = SpiritScore.objects.get_or_create(

            completed_matches = Match.objects.filter(tournament=tournament, status='completed')                    match=match,

            spirit_count = 0                    scoring_team=match.team_a,

                                receiving_team=match.team_b,

            for match in completed_matches:                    defaults={

                # Team A scores Team B                        'rules_knowledge': random.randint(2, 4),

                spirit1, created = SpiritScore.objects.get_or_create(                        'fouls_and_contact': random.randint(2, 4),

                    match=match,                        'fair_mindedness': random.randint(2, 4),

                    scoring_team=match.team_a,                        'positive_attitude': random.randint(2, 4),

                    receiving_team=match.team_b,                        'communication': random.randint(2, 4),

                    defaults={                        'comments': 'Great sportsmanship and communication!',

                        'rules_knowledge': random.randint(2, 4),                        'is_submitted': True,

                        'fouls_and_contact': random.randint(2, 4),                        'submitted_by': match.team_a.captain

                        'fair_mindedness': random.randint(2, 4),                    }

                        'positive_attitude': random.randint(2, 4),                )

                        'communication': random.randint(2, 4),                if created:

                        'comments': 'Great sportsmanship and communication!',                    spirit_count += 1

                        'is_submitted': True,                

                        'submitted_by': match.team_a.captain                # Team B scores Team A

                    }                spirit2, created = SpiritScore.objects.get_or_create(

                )                    match=match,

                if created:                    scoring_team=match.team_b,

                    spirit_count += 1                    receiving_team=match.team_a,

                                    defaults={

                # Team B scores Team A                        'rules_knowledge': random.randint(2, 4),

                spirit2, created = SpiritScore.objects.get_or_create(                        'fouls_and_contact': random.randint(2, 4),

                    match=match,                        'fair_mindedness': random.randint(2, 4),

                    scoring_team=match.team_b,                        'positive_attitude': random.randint(2, 4),

                    receiving_team=match.team_a,                        'communication': random.randint(2, 4),

                    defaults={                        'comments': 'Excellent spirit throughout the match!',

                        'rules_knowledge': random.randint(2, 4),                        'is_submitted': True,

                        'fouls_and_contact': random.randint(2, 4),                        'submitted_by': match.team_b.captain

                        'fair_mindedness': random.randint(2, 4),                    }

                        'positive_attitude': random.randint(2, 4),                )

                        'communication': random.randint(2, 4),                if created:

                        'comments': 'Excellent spirit throughout the match!',                    spirit_count += 1

                        'is_submitted': True,            

                        'submitted_by': match.team_b.captain            # Update team spirit averages

                    }            for team in teams:

                )                team.update_spirit_average()

                if created:            

                    spirit_count += 1            self.stdout.write(self.style.SUCCESS(f'  ✅ Created {spirit_count} spirit scores'))

            

            # Update team spirit averages        # Step 8: Add tournament announcements

            for team in teams:        self.stdout.write('\n📝 Step 8: Creating Announcements...')

                team.update_spirit_average()        

                    announcements_data = [

            self.stdout.write(self.style.SUCCESS(f'  ✅ Created {spirit_count} spirit scores'))            ('Welcome to Y-Ultimate Championship 2025!', 'Tournament kicks off in 30 days. Make sure to register your team!', False),

            ('Spirit of the Game Workshop', 'Join us for a workshop on Spirit of the Game scoring. Date: TBD', False),

        # Step 8: Add tournament announcements            ('Registration Deadline Extended', 'We have extended the registration deadline by 5 days!', True),

        self.stdout.write('\n📝 Step 8: Creating Announcements...')        ]

                

        announcements_data = [        for title, message, is_urgent in announcements_data:

            ('Welcome to Y-Ultimate Championship 2025!', 'Tournament kicks off in 30 days. Make sure to register your team!', False),            TournamentAnnouncement.objects.get_or_create(

            ('Spirit of the Game Workshop', 'Join us for a workshop on Spirit of the Game scoring. Date: TBD', False),                tournament=tournament,

            ('Registration Deadline Extended', 'We have extended the registration deadline by 5 days!', True),                title=title,

        ]                defaults={

                            'message': message,

        for title, message, is_urgent in announcements_data:                    'is_urgent': is_urgent,

            TournamentAnnouncement.objects.get_or_create(                    'created_by': director

                tournament=tournament,                }

                title=title,            )

                defaults={        

                    'message': message,        self.stdout.write(self.style.SUCCESS(f'  ✅ Created {len(announcements_data)} announcements'))

                    'is_urgent': is_urgent,

                    'created_by': director        # Final summary

                }        self.stdout.write(self.style.SUCCESS('\n' + '='*70))

            )        self.stdout.write(self.style.SUCCESS('✅ SETUP COMPLETE! '))

                self.stdout.write(self.style.SUCCESS('='*70))

        self.stdout.write(self.style.SUCCESS(f'  ✅ Created {len(announcements_data)} announcements'))        

        self.stdout.write(self.style.SUCCESS('\n📊 TOURNAMENT DATA SUMMARY:'))

        # Final summary        self.stdout.write(f'  🏆 Tournament: {tournament.name}')

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))        self.stdout.write(f'  👥 Teams: {len(teams)}')

        self.stdout.write(self.style.SUCCESS('✅ SETUP COMPLETE! '))        self.stdout.write(f'  🏃 Players: {Player.objects.filter(tournament=tournament).count()}')

        self.stdout.write(self.style.SUCCESS('='*70))        self.stdout.write(f'  ⚽ Matches: {Match.objects.filter(tournament=tournament).count()}')

                self.stdout.write(f'  ⭐ Spirit Scores: {SpiritScore.objects.filter(match__tournament=tournament).count()}')

        self.stdout.write(self.style.SUCCESS('\n📊 TOURNAMENT DATA SUMMARY:'))        self.stdout.write(f'  📢 Announcements: {TournamentAnnouncement.objects.filter(tournament=tournament).count()}')

        self.stdout.write(f'  🏆 Tournament: {tournament.name}')        

        self.stdout.write(f'  👥 Teams: {len(teams)}')        self.stdout.write(self.style.SUCCESS('\n🔑 LOGIN CREDENTIALS:'))

        self.stdout.write(f'  🏃 Players: {Player.objects.filter(tournament=tournament).count()}')        self.stdout.write(self.style.SUCCESS(f'\n  Tournament Director:'))

        self.stdout.write(f'  ⚽ Matches: {Match.objects.filter(tournament=tournament).count()}')        self.stdout.write(f'    Username: director')

        self.stdout.write(f'  ⭐ Spirit Scores: {SpiritScore.objects.filter(match__tournament=tournament).count()}')        self.stdout.write(f'    Password: director123')

        self.stdout.write(f'  📢 Announcements: {TournamentAnnouncement.objects.filter(tournament=tournament).count()}')        self.stdout.write(f'    Token: {token.key}')

                

        self.stdout.write(self.style.SUCCESS('\n🔑 LOGIN CREDENTIALS:'))        self.stdout.write(self.style.SUCCESS(f'\n  Team Captains:'))

        self.stdout.write(self.style.SUCCESS(f'\n  Tournament Director:'))        for i, (team_name, captain_username, _) in enumerate(team_data):

        self.stdout.write(f'    Username: director')            self.stdout.write(f'    {team_name}: {captain_username} / password123')

        self.stdout.write(f'    Password: director123')        

        self.stdout.write(f'    Token: {token.key}')        self.stdout.write(self.style.SUCCESS('\n\n🌐 ACCESS POINTS:'))

                self.stdout.write(f'  Django Admin: http://127.0.0.1:8000/admin/')

        self.stdout.write(self.style.SUCCESS(f'\n  Team Captains:'))        self.stdout.write(f'  API Base URL: http://127.0.0.1:8000/api/')

        for i, (team_name, captain_username, _) in enumerate(team_data):        self.stdout.write(f'  Frontend: http://localhost:3000/')

            self.stdout.write(f'    {team_name}: {captain_username} / password123')        

                self.stdout.write(self.style.SUCCESS('\n\n📱 NEXT STEPS:'))

        self.stdout.write(self.style.SUCCESS('\n\n🌐 ACCESS POINTS:'))        self.stdout.write('  1. Login to Django Admin with director/director123')

        self.stdout.write(f'  Django Admin: http://127.0.0.1:8000/admin/')        self.stdout.write('  2. View all tournament data')

        self.stdout.write(f'  API Base URL: http://127.0.0.1:8000/api/')        self.stdout.write('  3. Test API endpoints')

        self.stdout.write(f'  Frontend: http://localhost:3000/')        self.stdout.write('  4. Build frontend pages!')

                

        self.stdout.write(self.style.SUCCESS('\n\n📱 NEXT STEPS:'))        self.stdout.write(self.style.SUCCESS('\n' + '='*70 + '\n'))

        self.stdout.write('  1. Login to Django Admin with director/director123')
        self.stdout.write('  2. View all tournament data')
        self.stdout.write('  3. Test API endpoints')
        self.stdout.write('  4. Build frontend pages!')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70 + '\n'))
