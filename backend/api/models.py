from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

# --- Profile Model ---
class Profile(models.Model):
    """Extends the default Django User model with tournament-related fields."""
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('coach', 'Coach'),
        ('tournament_director', 'Tournament Director'),
        ('volunteer', 'Volunteer'),
        ('spectator', 'Spectator'),
    ]
    
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('team_manager', 'Team Manager'),
        ('captain', 'Captain'),
        ('tournament_director', 'Tournament Director'),
        ('field_official', 'Field Official'),
        ('scoring_team', 'Scoring Team'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)
    
    # Tournament-related fields
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='student')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    team_name = models.CharField(max_length=255, blank=True, null=True)
    team_role = models.CharField(max_length=100, blank=True, null=True)  # Added for student team role
    coach_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Profile completion tracking
    profile_completed = models.BooleanField(default=False)
    
    # Google OAuth fields
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    google_email = models.EmailField(blank=True, null=True)
    google_access_token = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)

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


# =============================================================================
# TOURNAMENT MANAGEMENT SYSTEM MODELS
# =============================================================================

# --- Tournament Model ---
class Tournament(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('registration_open', 'Registration Open'),
        ('registration_closed', 'Registration Closed'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    FORMAT_CHOICES = [
        ('round_robin', 'Round Robin'),
        ('knockout', 'Knockout'),
        ('swiss', 'Swiss System'),
        ('hybrid', 'Hybrid'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rules = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    tournament_format = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='round_robin')
    max_teams = models.IntegerField(default=16)
    min_players_per_team = models.IntegerField(default=7)
    max_players_per_team = models.IntegerField(default=15)
    tournament_director = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='directed_tournaments')
    sponsors = models.TextField(blank=True)
    banner_image = models.ImageField(upload_to='tournaments/banners/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


# --- Field Model ---
class Field(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    location_details = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"


# --- Team Model ---
class Team(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='captained_teams')
    home_city = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stats
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    points_for = models.IntegerField(default=0)
    points_against = models.IntegerField(default=0)
    spirit_score_average = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('tournament', 'name')
        ordering = ['-wins', '-spirit_score_average']
    
    def update_spirit_average(self):
        """Calculate average spirit score received from all matches"""
        received_scores = SpiritScore.objects.filter(
            receiving_team=self,
            is_submitted=True
        ).aggregate(avg=Avg('total_score'))
        
        self.spirit_score_average = received_scores['avg'] or 0.0
        self.save()
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"


# --- Player Model ---
class Player(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-Binary'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player_registrations')
    
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    age = models.IntegerField()
    jersey_number = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=100, blank=True)  # Handler, Cutter, Defense, Hybrid
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('team', 'email')
    
    def __str__(self):
        return f"{self.full_name} - {self.team.name}"


# --- Match Model ---
class Match(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, related_name='matches')
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')
    
    match_number = models.IntegerField()
    round_number = models.IntegerField(default=1)
    match_date = models.DateField()
    start_time = models.TimeField()
    
    team_a_score = models.IntegerField(default=0)
    team_b_score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['match_date', 'start_time']
        verbose_name_plural = 'Matches'
    
    def get_winner(self):
        """Returns the winning team or None if it's a draw"""
        if self.team_a_score > self.team_b_score:
            return self.team_a
        elif self.team_b_score > self.team_a_score:
            return self.team_b
        return None
    
    def __str__(self):
        return f"Match {self.match_number}: {self.team_a.name} vs {self.team_b.name}"


# --- Spirit Score Model ---
class SpiritScore(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='spirit_scores')
    scoring_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='given_spirit_scores')
    receiving_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='received_spirit_scores')
    
    # Spirit Score Categories (0-4 points each, 2 is default)
    rules_knowledge = models.IntegerField(default=2)  # Rules Knowledge & Use
    fouls_and_contact = models.IntegerField(default=2)  # Fouls & Body Contact
    fair_mindedness = models.IntegerField(default=2)  # Fair-Mindedness
    positive_attitude = models.IntegerField(default=2)  # Positive Attitude & Self-Control
    communication = models.IntegerField(default=2)  # Communication
    
    total_score = models.IntegerField(default=10)  # Auto-calculated (max 20)
    comments = models.TextField(blank=True)
    
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_spirit_scores')
    is_submitted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('match', 'scoring_team', 'receiving_team')
    
    def save(self, *args, **kwargs):
        # Auto-calculate total score
        self.total_score = (
            self.rules_knowledge +
            self.fouls_and_contact +
            self.fair_mindedness +
            self.positive_attitude +
            self.communication
        )
        super().save(*args, **kwargs)
        
        # Update receiving team's average spirit score
        if self.is_submitted:
            self.receiving_team.update_spirit_average()
    
    def __str__(self):
        return f"{self.scoring_team.name} → {self.receiving_team.name}: {self.total_score}/20"


# --- Attendance Model ---
class Attendance(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='attendances')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='attendances', blank=True, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('player', 'match', 'date')
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.player.full_name} - {status} on {self.date}"


# --- Tournament Announcement Model ---
class TournamentAnnouncement(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_urgent = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.tournament.name}"


# --- Visitor Registration Model ---
class VisitorRegistration(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='visitors')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=100, blank=True)  # Spectator, Volunteer, Media, etc.
    registered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.tournament.name}"