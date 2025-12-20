from django.contrib import admin
from .models import Reservation

from django.utils.html import format_html
from django.urls import reverse
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    # Colonnes affichées
    list_display = (
        'id',
        'user',
        'book',
        'status',
        'position_in_queue',
        'reservation_date',
        'pickup_deadline',
        'is_expired_display',
        'days_until_deadline_display',
    )

    # Filtres
    list_filter = (
        'status',
        'reservation_date',
        'pickup_deadline',
    )

    # Recherche
    search_fields = (
        'user__username',
        'user__email',
        'book__title',
        'book__isbn',
    )

    # Ordre
    ordering = ('reservation_date',)

    # Champs en lecture seule
    readonly_fields = (
        'reservation_date',
        'position_in_queue',
    )

    # Organisation du formulaire
    fieldsets = (
        ('Utilisateur & Livre', {
            'fields': ('user', 'book')
        }),
        ('Statut de la réservation', {
            'fields': ('status',)
        }),
        ('File d’attente', {
            'fields': ('position_in_queue',)
        }),
        ('Dates', {
            'fields': ('reservation_date', 'pickup_deadline')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    # -------- Méthodes admin --------

    @admin.display(boolean=True, description="Expirée")
    def is_expired_display(self, obj):
        return obj.is_expired

    @admin.display(description="Jours restants")
    def days_until_deadline_display(self, obj):
        return obj.days_until_deadline

    # -------- Actions admin --------

    actions = ['mark_selected_as_ready', 'cancel_selected_reservations']

    @admin.action(description="Marquer comme prêt à récupérer")
    def mark_selected_as_ready(self, request, queryset):
        for reservation in queryset:
            reservation.mark_as_ready()

    @admin.action(description="Annuler les réservations sélectionnées")
    def cancel_selected_reservations(self, request, queryset):
        for reservation in queryset:
            reservation.cancel()
    def edit_button(self, obj):
        url = reverse('admin:reservations_reservation_change', args=[obj.id])
        return format_html(
            '<a class="button" href="{}">✏ Modifier</a>', url
        )
    edit_button.short_description = "Modifier"
    def delete_button(self, obj):
        url = reverse('admin:reservations_reservation_delete', args=[obj.id])
        return format_html(
            '<a class="button" style="color:red" href="{}">🗑 Supprimer</a>', url
        )
    delete_button.short_description = "Supprimer"
    list_display += ('edit_button', 'delete_button',)
    
