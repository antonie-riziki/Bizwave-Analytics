// Public Auth Token Manager
window.AuthService = {
  getToken() {
    return localStorage.getItem("access_token");
  },
  setToken(token) {
    localStorage.setItem("access_token", token);
  },
  clearToken() {
    localStorage.removeItem("access_token");
  },
  getAuthHeaders() {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  },
};
