from rest_framework import serializers
from .models import Reservation
from books.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer basique pour les réservations"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    is_expired = serializers.SerializerMethodField()
    days_until_deadline = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'user_username', 'book', 'book_title',
            'reservation_date', 'pickup_deadline', 'status',
            'position_in_queue', 'is_expired', 'days_until_deadline', 'notes'
        ]
        read_only_fields = [
            'id', 'reservation_date', 'user_username', 'book_title',
            'is_expired', 'days_until_deadline', 'position_in_queue'
        ]
        
    def get_is_expired(self, obj):
        return obj.is_expired


class ReservationDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les réservations"""
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'book', 'reservation_date', 'pickup_deadline',
            'status', 'position_in_queue', 'is_expired', 'days_until_deadline', 'notes'
        ]
        read_only_fields = [
            'id', 'reservation_date', 'is_expired', 'days_until_deadline',
            'position_in_queue'
        ]
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }
    
    def get_book(self, obj):
        return {
            'id': obj.book.id,
            'title': obj.book.title,
            'author': str(obj.book.author),
            'isbn': obj.book.isbn,
            'is_available': obj.book.is_available
        }
    
    def get_is_expired(self, obj):
        return obj.is_expired