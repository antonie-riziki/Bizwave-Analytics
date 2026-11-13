// Authentication & MFA Backend Integration
import { apiRequest } from "./config.js";

export async function login(email, password) {
  const data = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  if (data.access_token) {
    localStorage.setItem("access_token", data.access_token);
  }
  return data;
}

export async function signup(payload) {
  return apiRequest("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function verifyMfa(code, challengeToken) {
  return apiRequest("/auth/mfa/verify", {
    method: "POST",
    body: JSON.stringify({ code, challenge_token: challengeToken }),
  });
}
