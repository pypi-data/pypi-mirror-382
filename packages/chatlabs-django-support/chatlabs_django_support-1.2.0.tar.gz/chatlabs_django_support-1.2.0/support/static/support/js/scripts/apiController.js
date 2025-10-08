import { API_URL } from "../const/API_URL.js";
import {
    btnSetUnassignedTicketsElement,
    btnSetMyTicketsElement,
    ticketListElement,
} from "../const/ELEMENTS.js";
import { TICKETS_EVENTS } from "../const/TICKETS_EVENTS.js";
import { addTicketToList } from "../helpers/addTicketToList.js";
import { renderMessageList } from "../helpers/renderMessageList.js";
import { state } from "../state.js";

export function getTickets(managerId) {
    let url = API_URL + TICKETS_EVENTS.SEND.GET_TICKETS;
    if (managerId) {
        url += `?manager=${managerId}`;
        btnSetUnassignedTicketsElement.disabled = false;
        btnSetMyTicketsElement.disabled = true;
        btnSetUnassignedTicketsElement.classList.remove("!bg-gray-600");
        btnSetMyTicketsElement.classList.add("!bg-gray-600");
    } else {
        url += `?manager__isnull=true`;
        btnSetUnassignedTicketsElement.disabled = true;
        btnSetMyTicketsElement.disabled = false;
        btnSetUnassignedTicketsElement.classList.add("!bg-gray-600");
        btnSetMyTicketsElement.classList.remove("!bg-gray-600");
    }
    ticketListElement.innerHTML = "";
    fetch(url)
        .then((response) => response.json())
        .then((data) => data.forEach((item) => addTicketToList(item)))
        .catch((error) => console.error(error));
}

export function getTicketMessages(ticketId) {
    fetch(API_URL + TICKETS_EVENTS.SEND.GET_TICKET_MESSAGES(ticketId))
        .then((response) => response.json())
        .then((data) => {
            data.reverse();
            data.forEach((item) => state.addMessage(item));
            renderMessageList(state.getMessages());
        })
        .catch((error) => console.error(error));
}

export function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1] ?? "";
}

export async function setTicketViewed(ticketId) {
    const res = await fetch(API_URL + TICKETS_EVENTS.SEND.SET_TICKET_VIEWED(ticketId), {
        method: "PATCH",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken(), "X-Requested-With": "XMLHttpRequest" },
        body: JSON.stringify({ viewed: true }),
    });
    if (!res.ok) throw new Error("Failed to set viewed");

    try { return await res.json(); } catch { return null; }
}