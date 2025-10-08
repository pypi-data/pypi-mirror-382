from django.urls import path

from . import views

app_name = 'support'

urlpatterns = [
    path('manager/', views.Support.as_view(), name='manager'),
    path('tickets/', views.TicketList.as_view(), name='tickets'),
    path('tickets/<int:ticket_id>/', views.Ticket.as_view(), name='ticket'),
    path(
        'tickets/<int:ticket_id>/messages/',
        views.MessageList.as_view(),
        name='messages',
    ),
]
