from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Étudiant'),
        ('teacher', 'Enseignant'),
        ('librarian', 'Bibliothécaire'),
    )

    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # ID auto-incrémental par défaut
    # Django utilise id = models.AutoField(primary_key=True) automatiquement
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
