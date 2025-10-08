const BASE_PATH = window.BASE_PATH || "";
export const SOCKET_URL = `${window.location.origin.replace("http", "ws")}${BASE_PATH}/ws/support/manager/`;
