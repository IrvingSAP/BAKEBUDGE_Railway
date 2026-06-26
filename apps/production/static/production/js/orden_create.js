(() => {
  const form = document.getElementById("form-orden-create");
  if (!form) return;

  const recetaSelect = document.getElementById("receta_id");
  const lotesInput = document.getElementById("cantidad_lotes");
  const versionLabel = document.getElementById("version-label");
  const previewCosto = document.getElementById("preview-costo");
  const previewRendimiento = document.getElementById("preview-rendimiento");
  const previewPorcion = document.getElementById("preview-porcion");

  const previewData = JSON.parse(
    document.getElementById("recetas-preview-data")?.textContent || "{}"
  );

  function formatMoney(value) {
    const num = parseFloat(value);
    if (Number.isNaN(num)) return "—";
    return num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function updatePreview() {
    const recetaId = recetaSelect?.value;
    const data = recetaId ? previewData[recetaId] : null;
    const lotes = parseFloat(lotesInput?.value);

    if (!data) {
      if (versionLabel) versionLabel.textContent = "—";
      if (previewCosto) previewCosto.textContent = "—";
      if (previewRendimiento) previewRendimiento.textContent = "—";
      if (previewPorcion) previewPorcion.textContent = "—";
      return;
    }

    if (versionLabel) {
      versionLabel.textContent = `${data.version_etiqueta} (vigente)`;
    }

    if (Number.isNaN(lotes) || lotes <= 0) {
      if (previewCosto) previewCosto.textContent = "—";
      if (previewRendimiento) previewRendimiento.textContent = "—";
      if (previewPorcion) previewPorcion.textContent = "—";
      return;
    }

    const costoTotal = parseFloat(data.costo_total) * lotes;
    const rendimiento = parseFloat(data.rendimiento_cantidad) * lotes;
    const porcion = rendimiento > 0 ? costoTotal / rendimiento : 0;

    if (previewCosto) previewCosto.textContent = formatMoney(costoTotal);
    if (previewRendimiento) {
      previewRendimiento.textContent = `${rendimiento} ${data.rendimiento_unidad}`;
    }
    if (previewPorcion) previewPorcion.textContent = formatMoney(porcion);
  }

  recetaSelect?.addEventListener("change", updatePreview);
  lotesInput?.addEventListener("input", updatePreview);
  updatePreview();

  form.addEventListener("submit", (event) => {
    if (!recetaSelect?.value) {
      event.preventDefault();
      if (globalThis.BakeBudgeModal?.showError) {
        globalThis.BakeBudgeModal.showError("Selecciona una receta.");
      } else {
        window.alert("Selecciona una receta.");
      }
      recetaSelect?.focus();
    }
  });
})();
