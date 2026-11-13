// Backend API Configuration
export const CONFIG = {
  API_BASE_URL: import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  WS_URL: import.meta.env?.VITE_WS_URL || "ws://localhost:8000/ws",
};

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };
  const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    throw new Error(`API Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}
