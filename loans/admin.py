from django.contrib import admin
from .models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste
    list_display = (
        'id',
        'user',
        'book',
        'status',
        'borrow_date',
        'due_date',
        'return_date',
        'is_overdue_display',
        'days_left_display',
    )

    # Filtres
    list_filter = (
        'status',
        'borrow_date',
        'due_date',
    )

    # Recherche
    search_fields = (
        'user__username',
        'user__email',
        'book__title',
        'book__isbn',
    )

    # Ordre par défaut
    ordering = ('-borrow_date',)

    # Champs non modifiables
    readonly_fields = (
        'borrow_date',
        'return_date',
        'renewed_count',
    )

    # Organisation du formulaire
    fieldsets = (
        ('Utilisateur & Livre', {
            'fields': ('user', 'book')
        }),
        ('Dates', {
            'fields': ('borrow_date', 'due_date', 'return_date')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Renouvellement', {
            'fields': ('renewable_count', 'renewed_count')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    # ----------- Méthodes affichage admin -----------

    @admin.display(boolean=True, description="En retard")
    def is_overdue_display(self, obj):
        return obj.is_overdue

    @admin.display(description="Jours restants")
    def days_left_display(self, obj):
        return obj.days_left
