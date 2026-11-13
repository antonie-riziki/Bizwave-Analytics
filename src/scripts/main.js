// Application Controller & Backend Wiring
import { apiRequest } from "./config.js";

const client = { request: apiRequest };

async function bootstrap() {
  const mainEl = document.querySelector("main[data-endpoint]");
  if (!mainEl) return;
  const endpoint = mainEl.getAttribute("data-endpoint");
  try {
    const payload = await client.request(endpoint);
    console.info("Backend payload loaded:", payload);
  } catch (error) {
    console.warn("Running in offline scaffold mode:", error.message);
  }
}

document.addEventListener("DOMContentLoaded", bootstrap);
