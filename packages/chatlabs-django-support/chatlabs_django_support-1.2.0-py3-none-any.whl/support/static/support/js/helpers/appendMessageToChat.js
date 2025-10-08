import { chatWindowElement } from "../const/ELEMENTS";

function appendMessageToChat(messageData) {
    const messageElement = createMessage(messageData);
    chatWindowElement.appendChild(messageElement);
    chatWindowElement.scrollTop = chatWindowElement.scrollHeight; // Прокрутка вниз
}