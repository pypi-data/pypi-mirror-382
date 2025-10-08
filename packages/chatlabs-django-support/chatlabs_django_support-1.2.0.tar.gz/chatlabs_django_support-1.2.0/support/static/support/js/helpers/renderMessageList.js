import { chatWindowElement } from "../const/ELEMENTS.js";
import { createMessage } from "./createMessage.js";
export function renderMessageList(messages) {
    chatWindowElement.innerHTML = ""; // Очистка чата
    console.log(messages)

    messages.forEach((message) => {
        const messageElement = createMessage(message);
        chatWindowElement.appendChild(messageElement);
    });

    chatWindowElement.scrollTop = chatWindowElement.scrollHeight;
}