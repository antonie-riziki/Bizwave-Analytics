// Public Entry Bootstrap
document.addEventListener("DOMContentLoaded", async () => {
  const baseUrl = window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${baseUrl}/health`, {
      headers: window.AuthService?.getAuthHeaders() || {},
    });
    document.body.dataset.backendStatus = res.ok ? "online" : "degraded";
  } catch {
    document.body.dataset.backendStatus = "offline";
  }
});
