// PrivacyTerms Component - Backend Integration Scaffold
export async function initPrivacyTerms(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/legal/terms");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[PrivacyTerms] Backend unavailable:", err.message);
    return null;
  }
}
