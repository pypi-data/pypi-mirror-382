import { TICKETS_EVENTS } from "../const/TICKETS_EVENTS.js";
import { addTicketToList } from "../helpers/addTicketToList.js";
import { renderMessageList } from "../helpers/renderMessageList.js";
import { updateTicketAssignment } from "../helpers/updateTicketAssignment.js";
import { state } from "../state.js";

export function controller(message, ws) {
    switch (message.type) {
        case TICKETS_EVENTS.RECEIVE.TICKET_CREATED:
            addTicketToList(message.ticket);
            break;
        case TICKETS_EVENTS.RECEIVE.TICKET_MESSAGE_NEW:
            console.log("Сообщение получено");
            if (message.message.ticket == state.getCurrentChatId()) {
                console.log("Сообщение должно отобразиться");
                state.addMessage(message.message);
                renderMessageList(state.getMessages());
            }
            break;
        case TICKETS_EVENTS.RECEIVE.TICKET_ASSIGNED:
            updateTicketAssignment(message);
            break;
        case TICKETS_EVENTS.SEND.TICKET_ASSIGN:
            ws.send(
                JSON.stringify({
                    type: TICKETS_EVENTS.SEND.TICKET_ASSIGN,
                    ticket_id: state.getCurrentChatId(),
                })
            );
            break;
        case TICKETS_EVENTS.SEND.TICKET_MESSAGE_NEW:
            if (message.text === "" || !state.getCurrentChatId()) break;
            ws.send(
                JSON.stringify({
                    type: TICKETS_EVENTS.SEND.TICKET_MESSAGE_NEW.split("_")[1],
                    ticket_id: state.getCurrentChatId(),
                    text: message.text,
                })
            );
    }
}
