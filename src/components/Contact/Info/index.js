// ContactInfo Component - Backend Integration Scaffold
export async function initContactInfo(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/contact/info");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[ContactInfo] Backend unavailable:", err.message);
    return null;
  }
}
