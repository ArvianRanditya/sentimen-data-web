import axios from "axios";

export const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// Buat instance Axios terpusat
const api = axios.create({
  baseURL,
});

export default api;
