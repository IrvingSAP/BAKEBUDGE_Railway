/** Validación mínima cliente — cabecera receta (create/edit). */
(() => {
  const form = document.querySelector(".recetas-form[data-bb-validate-form], .recetas-form");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    const nombre = form.querySelector("#nombre");
    if (nombre && !nombre.value.trim()) {
      event.preventDefault();
      if (window.BakeBudgeModal) {
        BakeBudgeModal.showError("El nombre de la receta es obligatorio.");
      }
      nombre.focus();
    }
  });
})();
