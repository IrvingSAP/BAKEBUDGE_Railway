(() => {
  const form = document.getElementById("form-recetaversion-create");
  if (!form) return;

  const DEMO = {
    1: {
      receta_id: 1,
      nombre: "Brownie clásico",
      version_origen: 2,
      rendimiento: "12 porciones",
      ingredientes_count: 6,
      pasos_count: 4,
      indirectos_count: 2,
      costo_total: "24.50",
      siguiente_version: 3,
    },
  };

  const params = new URLSearchParams(window.location.search);
  const recetaId = params.get("receta_id") || "1";
  const data = DEMO[recetaId];

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  if (!data) {
    BakeBudgeModal.showError(`Receta #${recetaId} no encontrada (demo).`);
    return;
  }

  form.receta_id.value = String(data.receta_id);
  setText("ctx-nombre", data.nombre);
  setText("src-version", `v${data.version_origen}`);
  setText("src-rendimiento", data.rendimiento);
  setText("src-ingredientes", String(data.ingredientes_count));
  setText("src-pasos", String(data.pasos_count));
  setText("src-indirectos", String(data.indirectos_count));
  setText("src-costo", `$ ${data.costo_total}`);
  setText("dest-version", `v${data.siguiente_version}`);

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const notas = form.notas_cambio.value.trim();
    if (!notas) {
      BakeBudgeModal.showError("Documenta el motivo del cambio en «Notas de cambio».");
      form.notas_cambio.focus();
      return;
    }
    const copiarIng = form.copiar_ingredientes.checked;
    const copiarPasos = form.copiar_pasos.checked;
    const copiarInd = form.copiar_indirectos.checked;
    if (!copiarIng && !copiarPasos && !copiarInd) {
      BakeBudgeModal.showError("Marca al menos una opción de copia (ingredientes, pasos o indirectos).");
      return;
    }
    const partes = [];
    if (copiarIng) partes.push("ingredientes");
    if (copiarPasos) partes.push("pasos");
    if (copiarInd) partes.push("indirectos");
    BakeBudgeModal.showSuccess(
      `Versión v${data.siguiente_version} creada desde v${data.version_origen} — «${data.nombre}» (demo). ` +
        `Copiado: ${partes.join(" + ")}.`
    );
  });
})();
