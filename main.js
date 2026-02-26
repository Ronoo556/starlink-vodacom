// ── Toast Notification ───────────────────────────────────────
let toastTimer;
function showToast(message, duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), duration);
}

// ── Mobile Nav Bottom Bar (if needed) ───────────────────────
// Highlight active link on mobile
document.querySelectorAll('.nav-link').forEach(link => {
  if (link.href === window.location.href) {
    link.classList.add('active');
  }
});
