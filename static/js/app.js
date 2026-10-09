// AJAX likes (progressive enhancement: forms still work without JS)
document.addEventListener("submit", async (e) => {
  const form = e.target.closest(".like-form");
  if (!form) return;
  e.preventDefault();
  const res = await fetch(form.action, {
    method: "POST",
    headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value },
  });
  if (res.ok) form.querySelector(".like-count").textContent = (await res.json()).count;
});

// Notifications: sadhe polling - dar 15 sec la server la vichara (WebSocket nahi, extra library nahi)
(function () {
  const badge = document.getElementById("notif-badge");
  if (!badge) return;
  let lastId = null;
  async function check() {
    try {
      const res = await fetch("/notifications/unread/" + (lastId !== null ? "?since=" + lastId : ""));
      if (!res.ok) return;
      const d = await res.json();
      badge.textContent = d.unread;
      badge.classList.toggle("d-none", d.unread === 0);
      const box = document.getElementById("toasts");
      d.new.forEach((n) => {
        const el = document.createElement("div");
        el.className = "toast show";
        el.innerHTML = '<div class="toast-body"><a href="" class="text-decoration-none"></a></div>';
        const a = el.querySelector("a");
        a.textContent = n.text; // textContent = XSS safe
        a.href = n.url;
        box.appendChild(el);
        setTimeout(() => el.remove(), 5000);
      });
      lastId = d.last_id;
    } catch (e) { /* network error - next time try again */ }
  }
  check();
  setInterval(check, 15000);
})();
