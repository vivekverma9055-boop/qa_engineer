(function () {
  const LINES = [
    { device: "web", text: "tests/web/test_checkout.py::test_add_to_cart", status: "pass" },
    { device: "api", text: "tests/api/test_endpoints.py::test_get_jobs", status: "pass" },
    { device: "android", text: "tests/mobile/test_android.py::test_login_flow", status: "pass" },
    { device: "ios", text: "tests/mobile/test_ios.py::test_push_notification", status: "fail" },
    { device: "hardware", text: "tests/device/test_camera_autofocus.py::test_focus_lock", status: "pass" },
    { device: "web", text: "tests/web/test_signup.py::test_email_validation", status: "pass" },
    { device: "api", text: "tests/api/test_endpoints.py::test_rate_limit", status: "pass" },
    { device: "android", text: "tests/mobile/test_android.py::test_offline_sync", status: "pass" },
  ];

  document.addEventListener("DOMContentLoaded", function () {
    const linesEl = document.getElementById("demoLines");
    const fillEl = document.getElementById("demoProgressFill");
    const passEl = document.getElementById("demoPassCount");
    const failEl = document.getElementById("demoFailCount");
    const deviceEls = document.querySelectorAll(".demo-device");

    if (!linesEl || !fillEl) return;

    let i = 0;
    let pass = 0;
    let fail = 0;
    let timer = null;
    let awaitingReset = false;

    function setActiveDevice(device) {
      deviceEls.forEach(function (el) {
        el.classList.toggle("active", el.dataset.device === device);
      });
    }

    function reset() {
      linesEl.innerHTML = "";
      fillEl.style.width = "0%";
      pass = 0;
      fail = 0;
      i = 0;
      passEl.textContent = "0";
      failEl.textContent = "0";
    }

    function step() {
      if (i >= LINES.length) {
        if (!awaitingReset) {
          awaitingReset = true;
          const summary = document.createElement("div");
          summary.className = "demo-line demo-summary";
          summary.textContent = pass + " passed, " + fail + " failed — report ready for review";
          linesEl.appendChild(summary);
          linesEl.scrollTop = linesEl.scrollHeight;
        }
        timer = setTimeout(function () {
          awaitingReset = false;
          reset();
          timer = setTimeout(step, 500);
        }, 2600);
        return;
      }

      const line = LINES[i];
      setActiveDevice(line.device);

      const el = document.createElement("div");
      const isFail = line.status === "fail";
      el.className = "demo-line " + (isFail ? "demo-fail-line" : "demo-pass-line");
      el.textContent = (isFail ? "✕ " : "✓ ") + line.text + (isFail ? " FAILED" : " PASSED");
      linesEl.appendChild(el);
      linesEl.scrollTop = linesEl.scrollHeight;

      if (isFail) {
        fail += 1;
        failEl.textContent = fail;
      } else {
        pass += 1;
        passEl.textContent = pass;
      }

      fillEl.style.width = Math.round(((i + 1) / LINES.length) * 100) + "%";
      i += 1;
      timer = setTimeout(step, 700);
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !timer) {
            step();
          } else if (!entry.isIntersecting && timer) {
            clearTimeout(timer);
            timer = null;
          }
        });
      },
      { threshold: 0.3 }
    );
    observer.observe(document.getElementById("demo") || linesEl);
  });
})();
