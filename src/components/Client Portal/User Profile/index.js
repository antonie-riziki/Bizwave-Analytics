// UserProfile Component - Backend Integration Scaffold
export async function initUserProfile(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/portal/profile");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[UserProfile] Backend unavailable:", err.message);
    return null;
  }
}
