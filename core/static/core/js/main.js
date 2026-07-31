document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("navToggle");
  var nav = document.getElementById("siteNav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.toggle("open");
    });
    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
      });
    });
  }

  var floatingCta = document.querySelector(".floating-cta");
  var contactSection = document.getElementById("contact");
  if (floatingCta && contactSection) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          floatingCta.classList.toggle("visible", !entry.isIntersecting);
        });
      },
      { rootMargin: "-40% 0px -40% 0px" }
    );
    observer.observe(contactSection);
  }
});
