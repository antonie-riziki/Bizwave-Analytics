// DocumentUpload Component - Backend Integration Scaffold
export async function initDocumentUpload(container, apiClient) {
  if (!container) return;
  try {
    const data = await apiClient.request("/portal/documents");
    container.dataset.status = "connected";
    return data;
  } catch (err) {
    container.dataset.status = "offline";
    console.warn("[DocumentUpload] Backend unavailable:", err.message);
    return null;
  }
}
