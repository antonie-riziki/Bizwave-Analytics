// Public Client-Side Route Guard & Navigation
window.Router = {
  routes: {
    "/": "/src/client_portal/index.html",
    "/process": "/src/client_portal/process.html",
    "/privacy": "/src/client_portal/privacy.html",
    "/portal": "/src/client_portal/client-portal.html",
    "/api": "/src/client_portal/api.html",
    "/auth": "/src/client_portal/auth.html",
    "/contact": "/src/client_portal/contact.html",
  },
  navigate(path) {
    window.location.href = this.routes[path] || this.routes["/"];
  },
};
