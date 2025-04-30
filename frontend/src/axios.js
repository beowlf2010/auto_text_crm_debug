// frontend/src/axios.js
import axios from "axios";

/* --------------- helpers --------------- */
function getCsrfToken() {
  // Django sets “csrftoken=<token>” in a cookie; grab it when it exists
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

/* --------------- instance --------------- */
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost", // defaults to port 80
  withCredentials: true, // ⇢ send session / CSRF cookies
});

/* --------------- interceptor --------------- */
api.interceptors.request.use((config) => {
  // For any state‑changing verb, attach X‑CSRFToken
  if (!/^(get|head|options)$/i.test(config.method || "")) {
    const token = getCsrfToken();
    if (token) config.headers["X-CSRFToken"] = token;
  }
  return config;
});

export default api;
