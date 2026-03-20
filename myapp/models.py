# models.py

from django.db import models

class Player(models.Model):
    SPORT_CHOICES = [
        ('mlb', 'MLB'),
        ('nfl', 'NFL'),
    ]
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES, default='mlb')
    name = models.CharField(max_length=100)
    stats = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.sport})"
    
class TriviaCategory(models.Model):
    SPORT_CHOICES = [
        ('mlb', 'MLB'),
        ('nfl', 'NFL'),
    ]
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES, default='mlb')
    title = models.CharField(max_length=100)
    description = models.TextField()
    stat_code = models.CharField(max_length=50, unique=True)
    recommended_pinpoint = models.IntegerField(null=True, blank=True)
    total_players = models.IntegerField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    players = models.ManyToManyField(Player, blank=True, related_name='trivia_categories')

    def __str__(self):
        return f"{self.get_sport_display()} — {self.title}"