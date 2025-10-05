/* js/main.js */
document.addEventListener("DOMContentLoaded", function () {
  // Mobile Navigation Toggle
  const mobileNavToggle = document.querySelector(".mobile-nav-toggle");
  const navLinks = document.querySelector(".nav-links");
  const body = document.body;

  // Create overlay element
  const navOverlay = document.createElement("div");
  navOverlay.className = "nav-overlay";
  document.body.appendChild(navOverlay);

  // Toggle navigation when hamburger icon is clicked
  mobileNavToggle.addEventListener("click", function () {
    toggleNavigation();
  });

  // Close navigation when overlay is clicked
  navOverlay.addEventListener("click", function () {
    if (navLinks.classList.contains("active")) {
      toggleNavigation();
    }
  });

  // Close navigation when a link is clicked
  document.querySelectorAll(".nav-links a").forEach((link) => {
    link.addEventListener("click", function () {
      if (window.innerWidth <= 768 && navLinks.classList.contains("active")) {
        toggleNavigation();
      }
    });
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
