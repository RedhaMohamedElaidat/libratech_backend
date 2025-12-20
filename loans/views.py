from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .models import Loan
from .serializers import LoanSerializer, LoanDetailSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class LoanPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class LoanViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les emprunts"""
    permission_classes = [AllowAny]
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    pagination_class = LoanPagination
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'user']
    search_fields = ['book__title', 'user__username']
    ordering_fields = ['borrow_date', 'due_date']
    ordering = ['-borrow_date']
    
    def get_queryset(self):
        """Retourner les emprunts selon l'utilisateur"""
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return Loan.objects.all()
            return Loan.objects.filter(user=user)
        # Pour les utilisateurs anonymes, retourner tous les emprunts actifs
        return Loan.objects.filter(status='active').order_by('-borrow_date')

    def get_serializer_class(self):
        """Utiliser un serializer détaillé pour retrieve"""
        if self.action == 'retrieve':
            return LoanDetailSerializer
        return LoanSerializer

    def perform_create(self, serializer):
        """Créer un emprunt avec l'utilisateur connecté"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()  # pour AllowAny, sans user

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def renew(self, request, pk=None):
        """Renouveler un emprunt"""
        loan = self.get_object()
        
        if loan.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'Vous ne pouvez renouveler que vos propres emprunts.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if loan.renew():
            serializer = self.get_serializer(loan)
            return Response(
                {'message': 'Emprunt renouvelé avec succès', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Impossible de renouveler cet emprunt.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def return_book(self, request, pk=None):
        """Retourner un emprunt sans authentification"""
        loan = self.get_object()

        if loan.status == 'returned':
            return Response(
                {'detail': 'Ce livre a déjà été retourné.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        loan.return_book()  # ici tu mets juste à jour le statut
        serializer = self.get_serializer(loan)
        return Response(
            {'message': 'Livre retourné avec succès', 'data': serializer.data},
            status=status.HTTP_200_OK
        )


    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_loans(self, request):
        """Récupérer les emprunts de l'utilisateur connecté"""
        loans = Loan.objects.filter(user=request.user).order_by('-borrow_date')
        page = self.paginate_queryset(loans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def overdue_loans(self, request):
        """Récupérer les emprunts en retard"""
        loans = Loan.objects.filter(
            user=request.user,
            status='active',
            due_date__lt=timezone.now()
        ).order_by('due_date')
        
        page = self.paginate_queryset(loans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
