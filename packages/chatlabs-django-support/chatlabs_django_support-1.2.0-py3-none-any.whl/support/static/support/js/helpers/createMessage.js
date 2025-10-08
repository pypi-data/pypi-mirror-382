import { createElement } from "./createElement.js";

/**
 * Создаёт DOM-элемент сообщения на основе переданного объекта сообщения.
 * @param {Object} messageObj - Объект сообщения.
 * @param {number} messageObj.id - ID сообщения.
 * @param {string} messageObj.created_at - Дата создания сообщения.
 * @param {"user" | "supp"} messageObj.sender - Отправитель сообщения.
 * @param {string} messageObj.text - Текст сообщения.
 * @param {boolean} messageObj.viewed - Флаг, указывающий, просмотрено ли сообщение.
 * @param {number} messageObj.ticket - ID тикета.
 * @returns {HTMLElement} - DOM-элемент сообщения.
 */
export function createMessage(messageObj) {
    const { sender, text, created_at } = messageObj;

    const messageClasses = ["mb-[15px]", "p-[10px]", "rounded-lg", "w-fit"];
    if (sender === "user") {
        messageClasses.push("bg-[#111827]", "mr-auto");
    } else if (sender === "supp") {
        messageClasses.push("bg-purple-600", "ml-auto");
    }

    const textElements = text.split("\n").map((line) =>
        createElement("span", {
            textContent: line,
            classes: ["block"],
        })
    );

    // Создаём элемент сообщения
    return createElement("div", {
        classes: messageClasses,
        children: [
            createElement("strong", {
                textContent: sender === "user" ? "Пользователь" : "Менеджер",
                classes: ["text-white/50"],
            }),
            createElement("p", {
                children: textElements,
                classes: ["text-white"],
            }),
            createElement("small", {
                textContent: new Date(created_at).toLocaleString(),
                classes: ["text-white/50"],
            }),
        ],
    });
}
