from django.db import models
from django.contrib.auth import get_user_model
from books.models import Book
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Loan(models.Model):
    """Modèle pour les emprunts de livres"""
    
    STATUS_CHOICES = (
        ('active', 'En cours'),
        ('returned', 'Retourné'),
        ('overdue', 'En retard'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    renewable_count = models.IntegerField(default=2)
    renewed_count = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-borrow_date']
    
    def save(self, *args, **kwargs):
        # Définir la date d'échéance à 14 jours
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=14)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.status == 'active' and timezone.now() > self.due_date:
            return True
        return False
    
    @property
    def days_left(self):
        if self.status == 'active':
            days = (self.due_date - timezone.now()).days
            return max(0, days)
        return 0
    
    @property
    def can_renew(self):
        """Vérifier si l'emprunt peut être renouvelé"""
        return self.renewed_count < self.renewable_count and self.status == 'active'
    
    def renew(self):
        """Renouveler l'emprunt pour 14 jours supplémentaires"""
        if self.can_renew:
            self.due_date = timezone.now() + timedelta(days=14)
            self.renewed_count += 1
            self.save()
            return True
        return False
    
    def return_book(self):
        """Marquer le livre comme retourné"""
        self.return_date = timezone.now()
        self.status = 'returned'
        self.book.is_available = True
        self.book.save()
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"