from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DateTimeField, F, OuterRef, Subquery
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.pagination import LimitOffsetPagination

from . import filters, models, serializers


class Support(LoginRequiredMixin, TemplateView):
    template_name = 'support/support_manager.html'
    login_url = '/admin/login/'


class TicketList(ListCreateAPIView):
    queryset = models.Ticket.objects.none()
    serializer_class = serializers.Ticket
    filter_backends = [
        DjangoFilterBackend,  # pyright: ignore[reportAssignmentType]
    ]
    filterset_class = filters.Ticket

    def get_queryset(self):
        # Подзапрос: получить created_at последнего сообщения
        last_message_subquery = (
            models.Message.objects.filter(ticket=OuterRef('pk'))
            .order_by('-created_at')
            .values('created_at')[:1]
        )

        return models.Ticket.objects.annotate(
            last_message_created_at=Subquery(
                last_message_subquery, output_field=DateTimeField()
            )
        ).order_by(
            F('viewed').asc(),  # непросмотренные (False) первыми
            F('resolved').asc(),  # нерешённые первыми
            F('last_message_created_at').desc(nulls_last=True),
            F('created_at').desc(nulls_last=True),
        )


class Ticket(RetrieveUpdateAPIView):
    queryset = models.Ticket.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'ticket_id'
    serializer_class = serializers.Ticket


class MessageList(ListCreateAPIView):
    serializer_class = serializers.Message
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return models.Message.objects.filter(
            ticket__id=self.kwargs['ticket_id']
        ).order_by('-created_at')

    def perform_create(self, serializer: serializer_class):
        ticket = models.Ticket.objects.get(id=self.kwargs['ticket_id'])
        ticket.viewed = False
        ticket.save(update_fields=['viewed'])
        serializer.save(ticket=ticket)
