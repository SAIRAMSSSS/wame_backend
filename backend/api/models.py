from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Profile Model ---
class Profile(models.Model):
    """Extends the default Django User model for Y-Ultimate."""
    USER_TYPES = (
        ('student', 'Student'),
        ('coach', 'Coach'),
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
        ('tournament_director', 'Tournament Director'),
        ('team_manager', 'Team Manager'),
        ('referee', 'Referee'),
        ('scorer', 'Scorer'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    role = models.CharField(max_length=50, blank=True, null=True)  # Alternative role field for compatibility
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Team and Coach Information (for students)
    coach_name = models.CharField(max_length=255, blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    team_role = models.CharField(max_length=100, blank=True, null=True)  # e.g., Handler, Cutter, Defense
    
    # Profile completion tracking
    profile_completed = models.BooleanField(default=False)
    
    # Fitness tracking
    total_points = models.IntegerField(default=0)
    
    # Google OAuth fields
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    google_email = models.EmailField(blank=True, null=True)
    google_access_token = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)
    google_token_expiry = models.DateTimeField(blank=True, null=True)
    
    # Supabase Storage field configuration (requires django-storages setup)
    profile_picture = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

# Signal to automatically create a Profile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# --- Workout Model ---
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.name} by {self.user.username}"


# --- Exercise Model ---
class Exercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sets = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField(default=1)
    duration_minutes = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} in {self.workout.name}"


# --- Posture Analysis Model ---
class PostureAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    workout = models.ForeignKey(Workout, on_delete=models.SET_NULL, null=True, blank=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Store the path to the analyzed media (for reference)
    media_url = models.URLField()
    
    # Store the JSON data from MediaPipe analysis
    analysis_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for {self.user.username} on {self.created_at.date()}"


# --- FITNESS TRACKING FOR STUDENTS ---
class FitnessLog(models.Model):
    """Daily fitness tracking for students"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fitness_logs')
    date = models.DateField(auto_now_add=True)
    calories_burned = models.IntegerField(default=0)
    steps = models.IntegerField(default=0)
    active_minutes = models.IntegerField(default=0)
    distance_km = models.FloatField(default=0)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


# --- TOURNAMENT MANAGEMENT SYSTEM ---

class Tournament(models.Model):
    """Complete tournament management with all features"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('registration_open', 'Registration Open'),
        ('registration_closed', 'Registration Closed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    FORMAT_CHOICES = (
        ('round_robin', 'Round Robin'),
        ('single_elimination', 'Single Elimination'),
        ('double_elimination', 'Double Elimination'),
        ('pool_play', 'Pool Play'),
    )
    
    # Basic Info
    name = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()
    
    # Status & Format
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    tournament_format = models.CharField(max_length=30, choices=FORMAT_CHOICES, default='round_robin')
    
    # Capacity & Settings
    max_teams = models.IntegerField(default=16)
    min_players_per_team = models.IntegerField(default=7)
    max_players_per_team = models.IntegerField(default=15)
    
    # Branding & Media
    banner_image = models.ImageField(upload_to='tournaments/banners/', blank=True, null=True)
    sponsors = models.TextField(blank=True, null=True, help_text="Comma-separated sponsor names")
    
    # Admin
    tournament_director = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='directed_tournaments')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    def get_registered_teams_count(self):
        return self.teams.filter(status='approved').count()
    
    def get_total_players_count(self):
        approved_teams = self.teams.filter(status='approved')
        return sum(team.players.count() for team in approved_teams)


class Field(models.Model):
    """Playing fields within a tournament"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)  # e.g., "Field 1", "Main Field"
    location_details = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.tournament.name} - {self.name}"


class Team(models.Model):
    """Teams registered for tournaments"""
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captained_teams')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_teams')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Team Details
    home_city = models.CharField(max_length=255, blank=True, null=True)
    team_logo = models.ImageField(upload_to='teams/logos/', blank=True, null=True)
    
    # Stats (auto-calculated)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    points_for = models.IntegerField(default=0)
    points_against = models.IntegerField(default=0)
    average_spirit_score = models.FloatField(default=0.0)
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tournament', 'name']
        ordering = ['-wins', '-average_spirit_score']
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"
    
    def update_spirit_average(self):
        """Calculate average spirit score from all received scores"""
        received_scores = self.received_spirit_scores.filter(is_submitted=True)
        if received_scores.exists():
            total = sum(score.total_score for score in received_scores)
            self.average_spirit_score = total / received_scores.count()
            self.save()


class Player(models.Model):
    """Players linked to teams in tournaments"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    EXPERIENCE_CHOICES = (
        ('beginner', 'Beginner (0-1 years)'),
        ('intermediate', 'Intermediate (1-3 years)'),
        ('advanced', 'Advanced (3-5 years)'),
        ('expert', 'Expert (5+ years)'),
    )
    
    # Link to User (if registered on platform)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player_profiles')
    
    # Team & Tournament
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='players')
    
    # Personal Info
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    
    # Player Details
    jersey_number = models.PositiveIntegerField(blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)  # Handler, Cutter, etc.
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    
    # Status
    is_verified = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tournament', 'email']
        ordering = ['jersey_number', 'full_name']
    
    def __str__(self):
        return f"{self.full_name} - {self.team.name}"


class Match(models.Model):
    """Individual matches in tournaments"""
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, related_name='matches')
    
    # Teams
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')
    
    # Schedule
    match_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    
    # Match Details
    round_number = models.IntegerField(default=1)  # Which round of tournament
    match_number = models.IntegerField()  # Match sequence number
    
    # Scores
    team_a_score = models.IntegerField(default=0)
    team_b_score = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Officials
    referee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='refereed_matches')
    scorer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scored_matches')
    
    # Media
    photos = models.JSONField(default=list, blank=True)  # List of photo URLs
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['match_date', 'start_time', 'field']
        verbose_name_plural = 'Matches'
    
    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name} - {self.match_date}"
    
    def get_winner(self):
        """Returns winning team or None if draw/not completed"""
        if self.status != 'completed':
            return None
        if self.team_a_score > self.team_b_score:
            return self.team_a
        elif self.team_b_score > self.team_a_score:
            return self.team_b
        return None  # Draw


class SpiritScore(models.Model):
    """Spirit of the Game scoring (5 categories, 0-4 each)"""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='spirit_scores')
    
    # Who gave the score
    scoring_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='given_spirit_scores')
    # Who received the score
    receiving_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='received_spirit_scores')
    
    # 5 Spirit Categories (0-4 scale, 2 is default)
    rules_knowledge = models.IntegerField(default=2, help_text="Rules Knowledge & Use (0-4)")
    fouls_and_contact = models.IntegerField(default=2, help_text="Fouls & Body Contact (0-4)")
    fair_mindedness = models.IntegerField(default=2, help_text="Fair-Mindedness (0-4)")
    positive_attitude = models.IntegerField(default=2, help_text="Positive Attitude & Self-Control (0-4)")
    communication = models.IntegerField(default=2, help_text="Communication (0-4)")
    
    # Comments
    comments = models.TextField(blank=True, null=True, help_text="Optional feedback")
    
    # Metadata
    is_submitted = models.BooleanField(default=False)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_spirit_scores')
    submitted_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['match', 'scoring_team', 'receiving_team']
    
    def __str__(self):
        return f"{self.scoring_team.name} → {self.receiving_team.name} ({self.total_score}/20)"
    
    @property
    def total_score(self):
        """Calculate total spirit score (max 20)"""
        return (self.rules_knowledge + self.fouls_and_contact + 
                self.fair_mindedness + self.positive_attitude + 
                self.communication)
    
    def save(self, *args, **kwargs):
        """Auto-update receiving team's average spirit score"""
        super().save(*args, **kwargs)
        if self.is_submitted:
            self.receiving_team.update_spirit_average()


class Attendance(models.Model):
    """Track player attendance per match or day"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='attendances')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True, related_name='attendances')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='attendances')
    
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    marked_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['player', 'match', 'date']
        ordering = ['date', 'player']
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.player.full_name} - {self.date} - {status}"


class TournamentAnnouncement(models.Model):
    """Real-time announcements for tournaments"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    is_urgent = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tournament.name} - {self.title}"


class VisitorRegistration(models.Model):
    """On-ground visitor tracking"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='visitors')
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    
    purpose = models.CharField(max_length=100, blank=True, null=True)  # Spectator, Media, Sponsor, etc.
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.tournament.name}"


# --- SCHEDULE MANAGEMENT ---
class Schedule(models.Model):
    """Practice sessions, workshops, and events"""
    EVENT_TYPES = (
        ('practice', 'Practice Session'),
        ('workshop', 'Workshop'),
        ('match', 'Match'),
        ('meeting', 'Meeting'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='practice')
    location = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    participants = models.ManyToManyField(User, related_name='schedules', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.date}"