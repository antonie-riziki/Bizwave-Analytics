// ApiConnectors Component - Backend Integration Scaffold
export async function initApiConnectors(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/developer/connectors");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[ApiConnectors] Backend unavailable:", err.message);
    return null;
  }
}
