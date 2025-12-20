from rest_framework import serializers
from .models import Loan
from books.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class LoanSerializer(serializers.ModelSerializer):
    """Serializer basique pour les emprunts"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_left = serializers.IntegerField(read_only=True)
    can_renew = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'id', 'user', 'user_username', 'book', 'book_title',
            'borrow_date', 'due_date', 'return_date', 'status',
            'renewable_count', 'renewed_count', 'is_overdue',
            'days_left', 'can_renew', 'notes'
        ]
        read_only_fields = [
            'id', 'borrow_date', 'return_date', 'user_username',
            'book_title', 'is_overdue', 'days_left', 'can_renew'
        ]
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_can_renew(self, obj):
        return obj.can_renew


class LoanDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les emprunts"""
    
    user = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_left = serializers.IntegerField(read_only=True)
    can_renew = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = [
            'id', 'user', 'book', 'borrow_date', 'due_date',
            'return_date', 'status', 'renewable_count', 'renewed_count',
            'is_overdue', 'days_left', 'can_renew', 'notes'
        ]
        read_only_fields = [
            'id', 'borrow_date', 'return_date', 'is_overdue',
            'days_left', 'can_renew'
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
    
    def get_is_overdue(self, obj):
        return obj.is_overdue
    
    def get_can_renew(self, obj):
        return obj.can_renew