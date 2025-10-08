export const state = {
    currentChatId: null,
    messages: [],
    setCurrentChatId: function(id) {
        this.currentChatId = id;
        this.messages = [];
    },
    getCurrentChatId: function() {
        return this.currentChatId;
    },
    addMessage: function(message) {
        this.messages.unshift(message);
    },
    getMessages: function() {
        return this.messages;
    }
}