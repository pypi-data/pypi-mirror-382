export const TICKETS_EVENTS = {
    SEND: {
        GET_TICKETS: "tickets/",
        SET_TICKET_VIEWED: (id) => `tickets/${id}/`,

        GET_TICKET_MESSAGES: (id) => `tickets/${id}/messages/`,
        TICKET_ASSIGN: "ticket.assign",
        TICKET_MESSAGE_NEW: "send_ticket.message.new",
    },
    RECEIVE: {
        TICKET_CREATED: "ticket.created",
        TICKET_ASSIGNED: "ticket.assigned",
        TICKET_MESSAGE_NEW: "ticket.message.new",
    }
};
