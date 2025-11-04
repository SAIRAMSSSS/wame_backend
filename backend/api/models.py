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
        ('field_official', 'Field Official'),
        ('scoring_tech', 'Scoring Tech Team'),
        ('sponsor', 'Sponsor/Partner'),
        ('spectator', 'Spectator/Fan'),
        ('programme_director', 'Programme Director'),
        ('programme_manager', 'Programme Manager'),
        ('session_facilitator', 'Session Facilitator'),
        ('reporting_team', 'Reporting/Data Team'),
        ('site_coordinator', 'Site Coordinator'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
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


# --- TOURNAMENT MANAGEMENT ---
class Tournament(models.Model):
    """Ultimate Frisbee tournaments"""
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    TOURNAMENT_TYPES = (
        ('single_elimination', 'Single Elimination'),
        ('double_elimination', 'Double Elimination'),
        ('round_robin', 'Round Robin'),
        ('pools_playoffs', 'Pools + Playoffs'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    rules = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    tournament_type = models.CharField(max_length=20, choices=TOURNAMENT_TYPES, default='single_elimination')
    registration_deadline = models.DateField()
    max_participants = models.IntegerField(default=100)
    max_teams = models.IntegerField(default=16)
    sponsors = models.TextField(blank=True)
    banner_image = models.ImageField(upload_to='tournaments/banners/', blank=True, null=True)
    notification_sent = models.BooleanField(default=False)

    # Tournament Director (admin who manages this tournament)
    director = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='directed_tournaments')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Field(models.Model):
    """Playing fields for tournaments"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.IntegerField(default=100)  # Max spectators
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"


class Team(models.Model):
    """Tournament teams"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=100)
    captain = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='captained_teams')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_teams')
    approved = models.BooleanField(default=False)
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tournament', 'name']

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"


class TeamPlayer(models.Model):
    """Players in teams"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    jersey_number = models.IntegerField(blank=True, null=True)
    is_captain = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.team.name}"


class TournamentRegistration(models.Model):
    """Student tournament registrations"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tournament_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ['tournament', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.tournament.name}"


class Match(models.Model):
    """Tournament matches"""
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches')
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_b')
    round_number = models.IntegerField(default=1)
    match_number = models.IntegerField(default=1)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Scores
    team_a_score = models.IntegerField(default=0)
    team_b_score = models.IntegerField(default=0)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')

    # Spirit scores (submitted after match)
    spirit_scores_submitted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_time']

    def __str__(self):
        return f"{self.team_a.name} vs {self.team_b.name} - {self.tournament.name}"


class SpiritScore(models.Model):
    """Spirit scores for matches (5 categories, 0-4 points each)"""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='spirit_scores')
    submitting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='submitted_spirit_scores')
    target_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='received_spirit_scores')

    # Spirit categories (0-4 points each)
    rules_knowledge = models.IntegerField(choices=[(i, i) for i in range(5)], default=2)
    fouls_body_contact = models.IntegerField(choices=[(i, i) for i in range(5)], default=2)
    fair_mindedness = models.IntegerField(choices=[(i, i) for i in range(5)], default=2)
    positive_attitude = models.IntegerField(choices=[(i, i) for i in range(5)], default=2)
    communication = models.IntegerField(choices=[(i, i) for i in range(5)], default=2)

    comments = models.TextField(blank=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_spirit_scores')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['match', 'submitting_team', 'target_team']

    @property
    def total_score(self):
        """Calculate total spirit score (max 20)"""
        return self.rules_knowledge + self.fouls_body_contact + self.fair_mindedness + self.positive_attitude + self.communication

    def __str__(self):
        return f"Spirit score: {self.submitting_team.name} → {self.target_team.name}"


class TournamentBracket(models.Model):
    """Tournament bracket structure"""
    tournament = models.OneToOneField(Tournament, on_delete=models.CASCADE, related_name='bracket')
    bracket_data = models.JSONField()  # Store bracket structure as JSON
    current_round = models.IntegerField(default=1)
    is_finalized = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bracket for {self.tournament.name}"


class Notification(models.Model):
    """Real-time notifications for users"""
    NOTIFICATION_TYPES = (
        ('tournament_update', 'Tournament Update'),
        ('match_scheduled', 'Match Scheduled'),
        ('score_update', 'Score Update'),
        ('spirit_score_submitted', 'Spirit Score Submitted'),
        ('registration_approved', 'Registration Approved'),
        ('announcement', 'Announcement'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True, blank=True)
    related_match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True, blank=True)
    related_team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"


# --- CHILD DEVELOPMENT PROGRAMME MODELS ---
class ChildProfile(models.Model):
    """Centralized child profiles for development programmes"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='child_profile')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    school = models.CharField(max_length=255, blank=True)
    community = models.CharField(max_length=255, blank=True)
    programme_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_children')

    # Transfer history
    previous_programmes = models.JSONField(default=list)  # List of previous programmes
    transfer_date = models.DateField(null=True, blank=True)

    # Dual programme tracking
    dual_programme = models.BooleanField(default=False)
    secondary_programme = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.school}"


class Session(models.Model):
    """Programme sessions (practices, workshops, etc.)"""
    SESSION_TYPES = (
        ('practice', 'Practice Session'),
        ('workshop', 'Workshop'),
        ('assessment', 'Assessment'),
        ('home_visit', 'Home Visit'),
        ('meeting', 'Meeting'),
    )

    title = models.CharField(max_length=255)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='practice')
    programme_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    location = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Coach/facilitator details
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='facilitated_sessions')
    coach_attendance = models.BooleanField(default=False)
    coaching_time_hours = models.FloatField(default=0)
    travel_time_hours = models.FloatField(default=0)

    # Community visit tracking
    community_visit = models.BooleanField(default=False)
    visit_location = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.title} - {self.date}"


class Attendance(models.Model):
    """Child attendance for sessions"""
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='attendances')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['child', 'session']

    def __str__(self):
        return f"{self.child.user.get_full_name()} - {self.session.title} ({'Present' if self.is_present else 'Absent'})"


class LifeSkillsAssessment(models.Model):
    """LSAS (Life Skills Assessment Scale) assessments"""
    ASSESSMENT_TYPES = (
        ('baseline', 'Baseline Assessment'),
        ('mid_term', 'Mid-term Assessment'),
        ('end_term', 'End-term Assessment'),
        ('follow_up', 'Follow-up Assessment'),
    )

    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    assessment_date = models.DateField()

    # Assessment scores (scale of 1-5 for each skill)
    communication = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    teamwork = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    leadership = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    problem_solving = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    self_confidence = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    discipline = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)

    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='conducted_assessments')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assessment_date']

    @property
    def total_score(self):
        scores = [self.communication, self.teamwork, self.leadership,
                 self.problem_solving, self.self_confidence, self.discipline]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) if valid_scores else 0

    def __str__(self):
        return f"{self.child.user.get_full_name()} - {self.assessment_type} ({self.assessment_date})"


class HomeVisit(models.Model):
    """Home visit records for child development tracking"""
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='home_visits')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name='home_visits')
    visit_date = models.DateField()
    location = models.CharField(max_length=255)
    purpose = models.TextField()
    outcomes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"Home visit: {self.child.user.get_full_name()} - {self.visit_date}"


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