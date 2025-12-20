from rest_framework import viewsets, filters
from .models import Book
from .serializers import BookSerializer
from rest_framework.permissions import AllowAny

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'rating', 'created_at']
    ordering = ['-created_at']
    permission_classes=[AllowAny]
    