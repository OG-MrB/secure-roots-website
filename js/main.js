/* js/main.js */
document.addEventListener("DOMContentLoaded", function () {
  // Mobile Navigation Toggle
  const mobileNavToggle = document.querySelector(".mobile-nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  const body = document.body;

  // iOS fix: make the div behave as an interactive element
  mobileNavToggle.setAttribute("role", "button");
  mobileNavToggle.setAttribute("tabindex", "0");

  // Create overlay element
  const navOverlay = document.createElement("div");
  navOverlay.className = "nav-overlay";
  document.body.appendChild(navOverlay);

  // Toggle navigation — use touchend for iOS, click for desktop
  // Prevent ghost double-fires with a debounce flag
  let navToggleBusy = false;

  function handleToggle(e) {
    e.preventDefault();
    e.stopPropagation();
    if (navToggleBusy) return;
    navToggleBusy = true;
    toggleNavigation();
    setTimeout(function () { navToggleBusy = false; }, 300);
  }

  mobileNavToggle.addEventListener("touchend", handleToggle, { passive: false });
  mobileNavToggle.addEventListener("click", handleToggle);

  // Close navigation when overlay is tapped/clicked
  function handleOverlayClose(e) {
    e.preventDefault();
    if (navLinks.classList.contains("active")) {
      toggleNavigation();
    }
  }

  navOverlay.addEventListener("touchend", handleOverlayClose, { passive: false });
  navOverlay.addEventListener("click", handleOverlayClose);

  // Close navigation when a link is clicked/tapped
  document.querySelectorAll(".nav-links a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.innerWidth <= 768 && navLinks.classList.contains("active")) {
        toggleNavigation();
      }
    });
  });

  // Keyboard accessibility — toggle on Enter/Space
  mobileNavToggle.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggleNavigation();
    }
  });

  // Function to toggle navigation
  function toggleNavigation() {
    mobileNavToggle.classList.toggle("active");
    navLinks.classList.toggle("active");
    navOverlay.classList.toggle("active");
    body.classList.toggle("nav-open");
  }

  // Close navigation on window resize
  window.addEventListener("resize", function () {
    if (window.innerWidth > 768 && navLinks.classList.contains("active")) {
      mobileNavToggle.classList.remove("active");
      navLinks.classList.remove("active");
      navOverlay.classList.remove("active");
      body.classList.remove("nav-open");
    }
  });

  console.log("Secure Roots site loaded.");
});
