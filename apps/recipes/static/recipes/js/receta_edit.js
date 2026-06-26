(() => {
  const form = document.getElementById("form-receta-edit");
  if (!form) return;

  const demoRecetas = {
    1: {
      id: 1,
      nombre: "Brownie clásico",
      descripcion_corta: "Brownie húmedo con chocolate semi amargo",
      notas: "Usar molde 20×30 cm",
      status: "A",
      version: 2,
      rendimiento_cantidad: "12",
      rendimiento_unidad: "porciones",
      costo_total: "24.50",
      costo_porcion: "2.04",
      precio_sugerido: "2.86",
    },
  };

  function cargarDemo() {
    const params = new URLSearchParams(window.location.search);
    const pk = params.get("id") || form.pk.value || "1";
    const receta = demoRecetas[pk];
    if (!receta) {
      BakeBudgeModal.showError(`Receta #${pk} no encontrada (demo).`);
      return;
    }

    form.pk.value = String(receta.id);
    const pkDisplay = document.getElementById("pk_display");
    if (pkDisplay) pkDisplay.value = String(receta.id);

    form.nombre.value = receta.nombre;
    form.descripcion_corta.value = receta.descripcion_corta || "";
    form.notas.value = receta.notas || "";
    form.status.value = receta.status;

    const setStat = (id, text) => {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    };
    setStat("stat-version", `v${receta.version}`);
    setStat("stat-costo-total", `$ ${receta.costo_total}`);
    setStat("stat-costo-porcion", `$ ${receta.costo_porcion}`);
    setStat("stat-precio", `$ ${receta.precio_sugerido}`);
  }

  cargarDemo();

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const nombre = form.nombre.value.trim();

    if (!nombre) {
      BakeBudgeModal.showError("El nombre de la receta es obligatorio.");
      form.nombre.focus();
      return;
    }

    const activar = event.submitter?.name === "guardar_activar";
    if (activar) form.status.value = "A";

    BakeBudgeModal.showSuccess(`Receta #${form.pk.value} «${nombre}» actualizada (demo).`);
  });
})();
