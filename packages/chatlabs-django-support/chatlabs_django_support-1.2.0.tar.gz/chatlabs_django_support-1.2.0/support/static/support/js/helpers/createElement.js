/**
 * Создаёт DOM-элемент с заданными параметрами.
 * @param {string} tagName
 * @param {Object} [options]
 * @param {Object} [options.attributes]
 * @param {string|string[]} [options.classes]
 * @param {Node|Node[]} [options.children]
 * @param {Object} [options.styles]
 * @param {Object} [options.events]
 * @returns {HTMLElement}
 */
export function createElement(tagName, options = {}) {
    const element = document.createElement(tagName);

    // Установка атрибутов
    if (options.attributes) {
        for (const [key, value] of Object.entries(options.attributes)) {
            element.setAttribute(key, value);
        }
    }

    // Добавление классов
    if (options.classes) {
        const classList = Array.isArray(options.classes) ? options.classes : [options.classes];
        element.classList.add(...classList);
    }

    // Установка текстового содержимого
    if (options.textContent) {
        element.textContent = options.textContent;
    }

    // Вложенные элементы
    if (options.children) {
        const children = Array.isArray(options.children) ? options.children : [options.children];
        children.forEach(child => {
            if (child instanceof Node) {
                element.appendChild(child);
            }
        });
    }

    // Установка инлайн-стилей
    if (options.styles) {
        Object.assign(element.style, options.styles);
    }

    // Добавление событий
    if (options.events) {
        for (const [event, handler] of Object.entries(options.events)) {
            element.addEventListener(event, handler);
        }
    }

    return element;
}
