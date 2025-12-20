from django.contrib import admin
from .models import Book

from django.utils.html import format_html
from django.urls import reverse

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'status',
        'edit_button',
        'delete_button',
    )

    def edit_button(self, obj):
        url = reverse('admin:books_book_change', args=[obj.id])
        return format_html(
            '<a class="button" href="{}">✏ Modifier</a>', url
        )
    edit_button.short_description = "Modifier"

    def delete_button(self, obj):
        url = reverse('admin:books_book_delete', args=[obj.id])
        return format_html(
            '<a class="button" style="color:red" href="{}">🗑 Supprimer</a>', url
        )
    delete_button.short_description = "Supprimer"
