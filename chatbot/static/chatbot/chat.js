(function () {
  function getCookie(name) {
    const match = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return match ? match.pop() : "";
  }

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("chatToggle");
    const panel = document.getElementById("chatPanel");
    const close = document.getElementById("chatClose");
    const form = document.getElementById("chatForm");
    const input = document.getElementById("chatInput");
    const messages = document.getElementById("chatMessages");

    if (!toggle || !panel || !form) return;

    function openPanel() {
      panel.hidden = false;
      toggle.classList.add("is-open");
      input.focus();
    }
    function closePanel() {
      panel.hidden = true;
      toggle.classList.remove("is-open");
    }

    toggle.addEventListener("click", function () {
      panel.hidden ? openPanel() : closePanel();
    });
    close.addEventListener("click", closePanel);

    function addMessage(text, sender) {
      const el = document.createElement("div");
      el.className = "chat-msg chat-msg-" + sender;
      el.textContent = text;
      messages.appendChild(el);
      messages.scrollTop = messages.scrollHeight;
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      addMessage(text, "user");
      input.value = "";
      input.disabled = true;

      fetch("/chat/api/message/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ message: text }),
      })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          addMessage(data.reply || "Sorry, something went wrong. Please try again.", "bot");
        })
        .catch(function () {
          addMessage("Sorry, I couldn't reach the server. Please email vivkverma905@gmail.com directly.", "bot");
        })
        .finally(function () {
          input.disabled = false;
          input.focus();
        });
    });
  });
})();
