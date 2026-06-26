(() => {
  const form = document.getElementById("form-receta-create");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const nombre = form.nombre.value.trim();
    const rendimiento = parseFloat(form.rendimiento_cantidad.value);
    const rendimientoUnidad = form.rendimiento_unidad.value.trim();

    if (!nombre) {
      BakeBudgeModal.showError("El nombre de la receta es obligatorio.");
      form.nombre.focus();
      return;
    }
    if (nombre.length > 100) {
      BakeBudgeModal.showError("El nombre no puede superar 100 caracteres.");
      form.nombre.focus();
      return;
    }
    if (form.rendimiento_cantidad.value.trim() === "" || Number.isNaN(rendimiento) || rendimiento <= 0) {
      BakeBudgeModal.showError("El rendimiento debe ser un número mayor que 0.");
      form.rendimiento_cantidad.focus();
      return;
    }
    if (!rendimientoUnidad) {
      BakeBudgeModal.showError("Indica la unidad de rendimiento (porciones, unidades, moldes…).");
      form.rendimiento_unidad.focus();
      return;
    }

    const activar = event.submitter?.name === "guardar_activar";
    if (activar) {
      form.status.value = "A";
    }

    const estadoLabel = form.status.options[form.status.selectedIndex].text;
    BakeBudgeModal.showSuccess(
      `Receta «${nombre}» creada con versión v1 — ${rendimiento} ${rendimientoUnidad} (${estadoLabel}, demo).`
    );
  });
})();
