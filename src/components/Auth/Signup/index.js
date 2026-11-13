// AuthSignup Component - Backend Integration Scaffold
export async function initAuthSignup(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/auth/signup");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[AuthSignup] Backend unavailable:", err.message);
    return null;
  }
}
