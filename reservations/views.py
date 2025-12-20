from rest_framework import viewsets, status # type: ignore
from rest_framework.decorators import action # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore
from rest_framework.pagination import PageNumberPagination # type: ignore
from django.utils import timezone # type: ignore
from .models import Reservation
from .serializers import ReservationSerializer, ReservationDetailSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les réservations"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = ReservationPagination
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Retourner les réservations filtrées par utilisateur ou none si anonyme"""
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return Reservation.objects.all()
            return Reservation.objects.filter(user=user)
        # Pour les utilisateurs non connectés, ne rien retourner
        return Reservation.objects.none()

    def get_serializer_class(self):
        """Utiliser un serializer détaillé pour retrieve"""
        if self.action == 'retrieve':
            return ReservationDetailSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        """Créer une réservation avec l'utilisateur connecté"""
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def mark_as_ready(self, request, pk=None):
        """Marquer une réservation comme prête (staff only)"""
        reservation = self.get_object()
        if not request.user.is_staff:
            return Response(
                {'detail': 'Seul le personnel peut marquer comme prêt.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if reservation.mark_as_ready():
            serializer = self.get_serializer(reservation)
            return Response(
                {'message': 'Réservation marquée comme prête', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'detail': 'Impossible de marquer cette réservation comme prête.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def cancel(self, request, pk=None):
        """Annuler une réservation"""
        reservation = self.get_object()
        if reservation.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'Vous ne pouvez annuler que vos propres réservations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if reservation.status != 'pending':
            return Response(
                {'detail': 'Seules les réservations en attente peuvent être annulées.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservation.cancel()
        serializer = self.get_serializer(reservation)
        return Response(
            {'message': 'Réservation annulée avec succès', 'data': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def my_reservations(self, request):
        """Récupérer les réservations de l'utilisateur connecté"""
        reservations = Reservation.objects.filter(
            user=request.user
        ).order_by('position_in_queue')
        page = self.paginate_queryset(reservations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def ready_for_pickup(self, request):
        """Récupérer les réservations prêtes à récupérer"""
        reservations = Reservation.objects.filter(
            user=request.user,
            status='ready'
        ).order_by('pickup_deadline')
        page = self.paginate_queryset(reservations)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def queue_status(self, request):
        """Voir la file d'attente d'un livre (public)"""
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response(
                {'detail': 'book_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        reservations = Reservation.objects.filter(
            book_id=book_id,
            status='pending'
        ).order_by('position_in_queue')
        serializer = self.get_serializer(reservations, many=True)
        return Response({
            'book_id': book_id,
            'queue_length': reservations.count(),
            'queue': serializer.data
        })
