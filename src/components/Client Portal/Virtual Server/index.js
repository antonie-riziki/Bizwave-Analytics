// VirtualServer Component - Backend Integration Scaffold
export async function initVirtualServer(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/portal/servers");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[VirtualServer] Backend unavailable:", err.message);
    return null;
  }
}
