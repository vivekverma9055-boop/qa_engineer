(function () {
  const STEPS = [
    { icon: "📷", status: "Launching camera app…", item: "Camera app launches without crashing" },
    { icon: "🎯", status: "Checking autofocus…", item: "Autofocus locks on subject within 1 second" },
    { icon: "⚡", status: "Toggling flash modes…", item: "Flash (auto / on / off) switches correctly" },
    { icon: "🖼️", status: "Capturing a photo…", item: "Photo saves to gallery with correct orientation" },
    { icon: "🎥", status: "Recording a video…", item: "Video start/stop works, audio stays in sync" },
    { icon: "🔄", status: "Rotating the device…", item: "UI adapts correctly on screen rotation" },
    { icon: "🔐", status: "Checking permissions…", item: "Camera/storage permission prompts appear correctly" },
    { icon: "⬅️", status: "Pressing Android back…", item: "Back button returns to previous screen, no crash" },
    { icon: "📞", status: "Simulating interruption…", item: "Incoming call during capture doesn't lose the session" },
  ];

  document.addEventListener("DOMContentLoaded", function () {
    const iconEl = document.getElementById("phoneIcon");
    const statusEl = document.getElementById("phoneStatus");
    const listEl = document.getElementById("manualChecklist");
    const section = document.getElementById("manual-demo");

    if (!iconEl || !statusEl || !listEl || !section) return;

    STEPS.forEach(function (step) {
      const li = document.createElement("li");
      li.className = "checklist-item";
      li.innerHTML = '<span class="checklist-box"></span><span class="checklist-text">' + step.item + "</span>";
      listEl.appendChild(li);
    });
    const items = listEl.querySelectorAll(".checklist-item");

    let i = 0;
    let timer = null;

    function reset() {
      items.forEach(function (li) {
        li.classList.remove("done");
      });
      i = 0;
    }

    function step() {
      if (i >= STEPS.length) {
        statusEl.textContent = STEPS.length + "/" + STEPS.length + " checks completed ✅";
        iconEl.textContent = "✅";
        timer = setTimeout(function () {
          reset();
          timer = setTimeout(step, 400);
        }, 2600);
        return;
      }

      const current = STEPS[i];
      iconEl.textContent = current.icon;
      statusEl.textContent = current.status;
      items[i].classList.add("done");

      i += 1;
      timer = setTimeout(step, 900);
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
    observer.observe(section);
  });
})();
