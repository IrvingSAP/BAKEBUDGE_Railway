(() => {
  document.querySelectorAll("[data-ayuda-jump]").forEach((link) => {
    link.addEventListener("click", (e) => {
      const id = link.getAttribute("href")?.slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      target.classList.add("ayuda-section--highlight");
      window.setTimeout(() => target.classList.remove("ayuda-section--highlight"), 1200);
    });
  });
})();
