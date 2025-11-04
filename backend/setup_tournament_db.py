"""
Create tournament tables and populate with sample data
This script manually creates the missing tournament tables and adds sample data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

import sqlite3
from django.contrib.auth.models import User
from api.models import Profile
from rest_framework.authtoken.models import Token
from datetime import datetime, timedelta, date, time

print('🔧 Creating tournament tables...\n')

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

# Create Tournament table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_tournament (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rules TEXT,
    location VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    registration_deadline DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    tournament_format VARCHAR(50) DEFAULT 'round_robin',
    max_teams INTEGER DEFAULT 16,
    min_players_per_team INTEGER DEFAULT 7,
    max_players_per_team INTEGER DEFAULT 15,
    tournament_director_id INTEGER,
    sponsors TEXT,
    banner_image VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_director_id) REFERENCES auth_user(id)
)
''')

# Create Field table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_field (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    location_details TEXT,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id)
)
''')

# Create Team table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    captain_id INTEGER,
    home_city VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    points_for INTEGER DEFAULT 0,
    points_against INTEGER DEFAULT 0,
    spirit_score_average REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id),
    FOREIGN KEY (captain_id) REFERENCES auth_user(id),
    UNIQUE(tournament_id, name)
)
''')

# Create Player table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_player (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    user_id INTEGER,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(20),
    gender VARCHAR(20) NOT NULL,
    age INTEGER NOT NULL,
    jersey_number INTEGER,
    position VARCHAR(100),
    experience_level VARCHAR(20) DEFAULT 'beginner',
    is_verified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES api_team(id),
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    UNIQUE(team_id, email)
)
''')

# Create Match table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_match (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    field_id INTEGER,
    team_a_id INTEGER NOT NULL,
    team_b_id INTEGER NOT NULL,
    match_number INTEGER NOT NULL,
    round_number INTEGER DEFAULT 1,
    match_date DATE NOT NULL,
    start_time TIME NOT NULL,
    team_a_score INTEGER DEFAULT 0,
    team_b_score INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id),
    FOREIGN KEY (field_id) REFERENCES api_field(id),
    FOREIGN KEY (team_a_id) REFERENCES api_team(id),
    FOREIGN KEY (team_b_id) REFERENCES api_team(id)
)
''')

# Create SpiritScore table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_spiritscore (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    scoring_team_id INTEGER NOT NULL,
    receiving_team_id INTEGER NOT NULL,
    rules_knowledge INTEGER DEFAULT 2,
    fouls_and_contact INTEGER DEFAULT 2,
    fair_mindedness INTEGER DEFAULT 2,
    positive_attitude INTEGER DEFAULT 2,
    communication INTEGER DEFAULT 2,
    total_score INTEGER DEFAULT 10,
    comments TEXT,
    submitted_by_id INTEGER,
    is_submitted BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES api_match(id),
    FOREIGN KEY (scoring_team_id) REFERENCES api_team(id),
    FOREIGN KEY (receiving_team_id) REFERENCES api_team(id),
    FOREIGN KEY (submitted_by_id) REFERENCES auth_user(id),
    UNIQUE(match_id, scoring_team_id, receiving_team_id)
)
''')

# Create Attendance table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    match_id INTEGER,
    tournament_id INTEGER NOT NULL,
    date DATE NOT NULL,
    is_present BOOLEAN DEFAULT 0,
    marked_by_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES api_player(id),
    FOREIGN KEY (match_id) REFERENCES api_match(id),
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id),
    FOREIGN KEY (marked_by_id) REFERENCES auth_user(id),
    UNIQUE(player_id, match_id, date)
)
''')

# Create TournamentAnnouncement table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_tournamentannouncement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_urgent BOOLEAN DEFAULT 0,
    created_by_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id),
    FOREIGN KEY (created_by_id) REFERENCES auth_user(id)
)
''')

# Create VisitorRegistration table
cur.execute('''
CREATE TABLE IF NOT EXISTS api_visitorregistration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(20),
    purpose VARCHAR(100),
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES api_tournament(id)
)
''')

conn.commit()
print('✅ All tournament tables created successfully!\n')

# Now populate with sample data
print('📊 Populating tournament data...\n')

# Insert tournament
try:
    cur.execute('''
    INSERT INTO api_tournament (name, description, location, start_date, end_date, registration_deadline, status, tournament_format, max_teams, rules, sponsors)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Y-Ultimate Championship 2025',
        'The premier Ultimate Frisbee tournament featuring top teams from across India.',
        'Jawaharlal Nehru Stadium, Delhi',
        date.today().isoformat(),
        (date.today() + timedelta(days=3)).isoformat(),
        (date.today() - timedelta(days=7)).isoformat(),
        'ongoing',
        'round_robin',
        8,
        'Standard WFDF rules apply',
        'Nike, Adidas, Red Bull'
    ))
except sqlite3.OperationalError:
    # Fallback if column names differ
    cur.execute('''
    INSERT INTO api_tournament (name, description, location, start_date, end_date, registration_deadline, status, max_teams, rules, sponsors)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Y-Ultimate Championship 2025',
        'The premier Ultimate Frisbee tournament featuring top teams from across India.',
        'Jawaharlal Nehru Stadium, Delhi',
        date.today().isoformat(),
        (date.today() + timedelta(days=3)).isoformat(),
        (date.today() - timedelta(days=7)).isoformat(),
        'ongoing',
        8,
        'Standard WFDF rules apply',
        'Nike, Adidas, Red Bull'
    ))
tournament_id = cur.lastrowid
print(f'✅ Tournament created (ID: {tournament_id})')

# Insert fields
fields = []
for name, loc in [('Field A', 'North Section'), ('Field B', 'South Section'), ('Field C', 'East Section')]:
    cur.execute('INSERT INTO api_field (tournament_id, name, location_details, is_active) VALUES (?, ?, ?, ?)',
                (tournament_id, name, loc, 1))
    fields.append(cur.lastrowid)
print(f'✅ Created {len(fields)} fields')

# COMMIT AND CLOSE THE SQL CONNECTION BEFORE USING DJANGO ORM
conn.commit()
conn.close()
print('✅ SQL setup complete, switching to Django ORM for users...\n')

# Create captains and teams
teams_data = [
    ('Mumbai Thunderbolts', 'Mumbai', 'captain1', 'Raj', 'Sharma', 'raj.sharma@yultimate.com'),
    ('Delhi Dynamos', 'Delhi', 'captain2', 'Priya', 'Singh', 'priya.singh@yultimate.com'),
    ('Bangalore Blaze', 'Bangalore', 'captain3', 'Arjun', 'Patel', 'arjun.patel@yultimate.com'),
    ('Pune Phoenix', 'Pune', 'captain4', 'Neha', 'Gupta', 'neha.gupta@yultimate.com'),
]

# REOPEN CONNECTION FOR SQL OPERATIONS
conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

teams = []
for team_name, city, username, first, last, email in teams_data:
    # Create captain user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'first_name': first, 'last_name': last}
    )
    if created:
        user.set_password('password123')
        user.save()
        Profile.objects.get_or_create(user=user, defaults={'user_type': 'student', 'role': 'captain'})
        Token.objects.get_or_create(user=user)
    
    # Insert team
    cur.execute('''
        INSERT INTO api_team (tournament_id, name, captain_id, home_city, status, wins, losses, points_for, points_against)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tournament_id, team_name, user.id, city, 'approved', 0, 0, 0, 0))
    team_id = cur.lastrowid
    teams.append((team_id, team_name))
    
    # Create players for this team
    player_names = [
        ('Amit Kumar', 'male', 'Handler'), ('Sneha Reddy', 'female', 'Cutter'),
        ('Vikram Iyer', 'male', 'Hybrid'), ('Pooja Joshi', 'female', 'Deep'),
        ('Rahul Verma', 'male', 'Handler'), ('Anjali Nair', 'female', 'Cutter'),
        ('Karan Chopra', 'male', 'Hybrid'), ('Meera Desai', 'female', 'Deep')
    ]
    
    for i, (name, gender, position) in enumerate(player_names):
        email = f"{name.lower().replace(' ', '.')}@yultimate.com"
        cur.execute('''
            INSERT INTO api_player (team_id, tournament_id, full_name, email, phone, gender, age, jersey_number, position, experience_level, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (team_id, tournament_id, name, email, f'+91-9876{i:05d}', gender, 20+i, i+1, position, 'advanced' if i < 4 else 'intermediate', 1))

print(f'✅ Created {len(teams)} teams with 8 players each')

# Create matches with scores and spirit scores
match_count = 0
for i in range(len(teams)):
    for j in range(i+1, len(teams)):
        team_a_id, team_a_name = teams[i]
        team_b_id, team_b_name = teams[j]
        
        is_completed = match_count < 3
        status = 'completed' if is_completed else 'scheduled'
        ta_score = 13 if is_completed and match_count % 2 == 0 else 10 if is_completed else 0
        tb_score = 10 if is_completed and match_count % 2 == 0 else 13 if is_completed else 0
        match_time = datetime.now() + timedelta(hours=match_count * 2)
        
        cur.execute('''
            INSERT INTO api_match (tournament_id, field_id, team_a_id, team_b_id, match_number, round_number, match_date, start_time, status, team_a_score, team_b_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tournament_id, fields[match_count % len(fields)], team_a_id, team_b_id, match_count+1, 1, 
              match_time.date().isoformat(), match_time.time().isoformat(), status, ta_score, tb_score))
        match_id = cur.lastrowid
        
        # Update team stats for completed matches
        if is_completed:
            winner_id = team_a_id if ta_score > tb_score else team_b_id
            loser_id = team_b_id if winner_id == team_a_id else team_a_id
            
            cur.execute('UPDATE api_team SET wins = wins + 1, points_for = points_for + ?, points_against = points_against + ? WHERE id = ?',
                       (max(ta_score, tb_score), min(ta_score, tb_score), winner_id))
            cur.execute('UPDATE api_team SET losses = losses + 1, points_for = points_for + ?, points_against = points_against + ? WHERE id = ?',
                       (min(ta_score, tb_score), max(ta_score, tb_score), loser_id))
            
            # Create spirit scores
            cur.execute('''
                INSERT INTO api_spiritscore (match_id, scoring_team_id, receiving_team_id, rules_knowledge, fouls_and_contact, fair_mindedness, positive_attitude, communication, total_score, is_submitted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (match_id, team_a_id, team_b_id, 3, 4, 4, 3, 4, 18, 1))
            
            cur.execute('''
                INSERT INTO api_spiritscore (match_id, scoring_team_id, receiving_team_id, rules_knowledge, fouls_and_contact, fair_mindedness, positive_attitude, communication, total_score, is_submitted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (match_id, team_b_id, team_a_id, 4, 3, 3, 4, 3, 17, 1))
            
            # Update spirit averages
            cur.execute('SELECT AVG(total_score) FROM api_spiritscore WHERE receiving_team_id = ? AND is_submitted = 1', (team_a_id,))
            avg_a = cur.fetchone()[0] or 0
            cur.execute('UPDATE api_team SET spirit_score_average = ? WHERE id = ?', (avg_a, team_a_id))
            
            cur.execute('SELECT AVG(total_score) FROM api_spiritscore WHERE receiving_team_id = ? AND is_submitted = 1', (team_b_id,))
            avg_b = cur.fetchone()[0] or 0
            cur.execute('UPDATE api_team SET spirit_score_average = ? WHERE id = ?', (avg_b, team_b_id))
        
        match_count += 1

print(f'✅ Created {match_count} matches with spirit scores')

# Create announcements
announcements = [
    ('Welcome to Y-Ultimate Championship 2025!', 'Welcome message', 1),
    ('Schedule Update', 'Field B matches moved 30 min later', 0),
    ('Spirit Score Reminder', 'Please submit spirit scores within 30 minutes', 0),
]

for title, message, urgent in announcements:
    cur.execute('INSERT INTO api_tournamentannouncement (tournament_id, title, message, is_urgent) VALUES (?, ?, ?, ?)',
                (tournament_id, title, message, urgent))

print(f'✅ Created {len(announcements)} announcements')

conn.commit()
conn.close()

print('\n' + '='*60)
print('🎉 Tournament database setup complete!')
print('='*60)
print('\n📋 Sample Login Credentials:')
print('Team Captains:')
print('  captain1 / password123 (Mumbai Thunderbolts)')
print('  captain2 / password123 (Delhi Dynamos)')
print('  captain3 / password123 (Bangalore Blaze)')
print('  captain4 / password123 (Pune Phoenix)')
print('\nCoach:')
print('  coach_john_2024 / 12345')
print('\n✅ Backend: http://127.0.0.1:8000/')
print('✅ Frontend: http://localhost:3000/')
print('\nRun: python check_database.py to see all data\n')
