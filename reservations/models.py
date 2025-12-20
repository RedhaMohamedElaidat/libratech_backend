from django.db import models
from django.contrib.auth import get_user_model
from books.models import Book
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Reservation(models.Model):
    """Modèle pour les réservations de livres"""
    
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('ready', 'Prêt à récupérer'),
        ('cancelled', 'Annulée'),
        ('expired', 'Expirée'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    
    reservation_date = models.DateTimeField(auto_now_add=True)
    pickup_deadline = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    position_in_queue = models.IntegerField(default=1)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['reservation_date']
        unique_together = ('user', 'book')
    
    def save(self, *args, **kwargs):
        # Définir la date limite de récupération à 7 jours
        if not self.pickup_deadline:
            self.pickup_deadline = self.reservation_date + timedelta(days=7)
        
        # Calculer la position dans la file d'attente
        if not self.pk:
            self.position_in_queue = Reservation.objects.filter(
                book=self.book,
                status='pending'
            ).count() + 1
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Vérifier si la réservation a expiré"""
        if self.status == 'pending' and timezone.now() > self.pickup_deadline:
            return True
        return False
    
    @property
    def days_until_deadline(self):
        """Nombre de jours avant l'expiration"""
        if self.status in ['pending', 'ready']:
            days = (self.pickup_deadline - timezone.now()).days
            return max(0, days)
        return 0
    
    def mark_as_ready(self):
        """Marquer la réservation comme prête à récupérer"""
        if self.status == 'pending':
            self.status = 'ready'
            self.save()
            return True
        return False
    
    def cancel(self):
        """Annuler la réservation"""
        self.status = 'cancelled'
        self.save()
        # Mettre à jour la position des autres réservations
        self._update_queue_positions()
    
    def _update_queue_positions(self):
        """Mettre à jour les positions dans la file d'attente"""
        reservations = Reservation.objects.filter(
            book=self.book,
            status='pending'
        ).order_by('reservation_date')
        
        for index, reservation in enumerate(reservations, 1):
            reservation.position_in_queue = index
            reservation.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} (Position: {self.position_in_queue})"