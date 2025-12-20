from django.db import models

class Book(models.Model):
    """Modèle pour les livres"""
    
    STATUS_CHOICES = (
        ('available', 'Disponible'),
        ('borrowed', 'Emprunté'),
        ('reserved', 'Réservé'),
        ('maintenance', 'En maintenance'),
    )
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField(blank=True)
    pages = models.IntegerField()
    publication_year = models.IntegerField()
    category = models.CharField(max_length=100)
    language = models.CharField(max_length=50, default='French')
    
    # Gestion des copies
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    
    # Métadonnées
    rating = models.FloatField(default=0)
    reviews_count = models.IntegerField(default=0)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['isbn']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.author})"