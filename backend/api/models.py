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
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
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


# --- TOURNAMENT MANAGEMENT ---
class Tournament(models.Model):
    """Ultimate Frisbee tournaments"""
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    registration_deadline = models.DateField()
    max_participants = models.IntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name


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