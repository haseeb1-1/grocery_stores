// script.js
document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".btn");
  buttons.forEach((btn) => {
    btn.addEventListener("mouseenter", () => {
      btn.style.boxShadow = "0 8px 20px rgba(0,0,0,0.2)";
    });
    btn.addEventListener("mouseleave", () => {
      btn.style.boxShadow = "none";
    });
  });
});
