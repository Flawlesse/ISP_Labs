window.addEventListener("DOMContentLoaded", () => {
    setTimeout(function () {
      errors = document.querySelectorAll(".errorlist");
      errors.forEach((element) => {
        element.style.display = "none";
      });
    }, 5000);
  });