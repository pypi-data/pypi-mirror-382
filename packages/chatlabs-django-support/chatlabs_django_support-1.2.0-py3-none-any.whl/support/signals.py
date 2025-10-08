from . import models
from .consumers import ChatConsumer, ChatConsumerMessages
from asgiref.sync import async_to_sync


def post_save_ticket(sender, instance: models.Ticket, created: bool, **kwargs):  # noqa: ARG001
    if created:
        async_to_sync(ChatConsumer.get_channel_layer().group_send)(
            *ChatConsumerMessages.ticket_created(instance)
        )
        if instance.support_manager:
            async_to_sync(ChatConsumer.get_channel_layer().group_send)(
                *ChatConsumerMessages.ticket_assigned(
                    instance,
                    instance.support_manager,
                )
            )


def post_save_message(
    sender,  # noqa: ARG001
    instance: models.Message,
    created: bool,
    **kwargs,  # noqa: ARG001
):
    if created:
        async_to_sync(ChatConsumer.get_channel_layer().group_send)(
            *ChatConsumerMessages.ticket_message_new(instance)
        )
