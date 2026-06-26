(() => {
  const form = document.getElementById("form-recetaversion-edit");
  if (!form) return;

  const precioInput = document.getElementById("precio_venta_sugerido");
  const overrideInput = document.getElementById("precio_override_manual");

  const unidadesPorProducto = JSON.parse(
    document.getElementById("unidades-por-producto-data")?.textContent || "{}"
  );
  const unidadesGlobal = JSON.parse(
    document.getElementById("unidades-global-data")?.textContent || "[]"
  );
  const productosNombres = JSON.parse(
    document.getElementById("productos-nombres-data")?.textContent || "{}"
  );
  const indirectosNombres = JSON.parse(
    document.getElementById("indirectos-nombres-data")?.textContent || "{}"
  );

  function mensajeIndirectoDuplicado(gastoId) {
    const nombre = indirectosNombres[gastoId] || "Este gasto indirecto";
    return (
      `«${nombre}» ya está asignado en esta versión. ` +
      "Solo un registro por gasto; suma las cantidades en una sola línea."
    );
  }

  function mensajeProductoDuplicado(productoId) {
    const nombre = productosNombres[productoId] || "Este producto";
    return (
      `«${nombre}» ya está en la formulación. ` +
      "Solo un registro por producto; suma las cantidades en una sola línea."
    );
  }

  function avisar(mensaje, tipo = "warning") {
    const modal = globalThis.BakeBudgeModal;
    if (tipo === "error" && modal?.showError) {
      modal.showError(mensaje);
    } else if (modal?.showWarning) {
      modal.showWarning(mensaje);
    } else {
      window.alert(mensaje);
    }
  }

  function avisarProductoDuplicado(mensaje) {
    avisar(mensaje, "warning");
  }

  function getIngredienteRows() {
    return Array.from(document.querySelectorAll("#tbody-ingredientes tr.ingrediente-row"));
  }

  function filaIngredienteVacia(row) {
    const producto = row.querySelector('select[name="ingrediente_producto"]')?.value;
    const cantidad = row.querySelector('input[name="ingrediente_cantidad"]')?.value?.trim();
    const unidad = row.querySelector('select[name="ingrediente_unidad"]')?.value;
    const notas = row.querySelector('input[name="ingrediente_notas"]')?.value?.trim();
    return !producto && !cantidad && !unidad && !notas;
  }

  function validarFilaIngrediente(row, numeroFila) {
    const productoSel = row.querySelector('select[name="ingrediente_producto"]');
    const cantidadInp = row.querySelector('input[name="ingrediente_cantidad"]');
    const unidadSel = row.querySelector('select[name="ingrediente_unidad"]');

    if (!productoSel?.value) {
      avisar(`Selecciona el producto en la fila ${numeroFila}.`, "error");
      productoSel?.focus();
      return false;
    }

    const cantidad = parseFloat(cantidadInp?.value);
    if (!cantidadInp?.value?.trim() || Number.isNaN(cantidad) || cantidad <= 0) {
      avisar(`La cantidad debe ser mayor que 0 (fila ${numeroFila}).`, "error");
      cantidadInp?.focus();
      return false;
    }

    if (!unidadSel?.value) {
      avisar(`Selecciona la unidad en la fila ${numeroFila}.`, "error");
      unidadSel?.focus();
      return false;
    }

    return true;
  }

  function validarAntesDeAgregarIngrediente() {
    const rows = getIngredienteRows();
    if (rows.length === 0) {
      return true;
    }
    for (let i = 0; i < rows.length; i += 1) {
      const row = rows[i];
      if (filaIngredienteVacia(row)) {
        avisar(
          `Completa producto, cantidad y unidad en la fila ${i + 1} antes de agregar otra.`,
          "error"
        );
        row.querySelector('select[name="ingrediente_producto"]')?.focus();
        return false;
      }
      if (!validarFilaIngrediente(row, i + 1)) {
        return false;
      }
    }
    return true;
  }

  function validarTodasFilasIngredientes() {
    const rows = getIngredienteRows();
    const filasConDatos = rows.filter((row) => !filaIngredienteVacia(row));
    if (filasConDatos.length === 0) {
      avisar("Agrega al menos un ingrediente.", "error");
      return false;
    }
    for (let i = 0; i < rows.length; i += 1) {
      if (filaIngredienteVacia(rows[i])) {
        continue;
      }
      if (!validarFilaIngrediente(rows[i], i + 1)) {
        return false;
      }
    }
    return validarIngredientesSinDuplicados();
  }

  function getIndirectoRows() {
    return Array.from(document.querySelectorAll("#tbody-indirectos tr.indirecto-row"));
  }

  function filaIndirectoVacia(row) {
    const gasto = row.querySelector('select[name="indirecto_gasto"]')?.value;
    const cantidad = row.querySelector('input[name="indirecto_cantidad"]')?.value?.trim();
    const notas = row.querySelector('input[name="indirecto_notas"]')?.value?.trim();
    return !gasto && !cantidad && !notas;
  }

  function validarFilaIndirecto(row, numeroFila) {
    const gastoSel = row.querySelector('select[name="indirecto_gasto"]');
    const cantidadInp = row.querySelector('input[name="indirecto_cantidad"]');

    if (!gastoSel?.value) {
      avisar(`Selecciona el gasto indirecto en la fila ${numeroFila}.`, "error");
      gastoSel?.focus();
      return false;
    }

    const cantidad = parseFloat(cantidadInp?.value);
    if (cantidadInp?.value?.trim() === "" || Number.isNaN(cantidad) || cantidad < 0) {
      avisar(`La cantidad del indirecto debe ser ≥ 0 (fila ${numeroFila}).`, "error");
      cantidadInp?.focus();
      return false;
    }

    return true;
  }

  function validarAntesDeAgregarIndirecto() {
    const rows = getIndirectoRows();
    if (rows.length === 0) {
      return true;
    }
    for (let i = 0; i < rows.length; i += 1) {
      const row = rows[i];
      if (filaIndirectoVacia(row)) {
        avisar(
          `Completa gasto y cantidad en la fila ${i + 1} antes de agregar otra.`,
          "error"
        );
        row.querySelector('select[name="indirecto_gasto"]')?.focus();
        return false;
      }
      if (!validarFilaIndirecto(row, i + 1)) {
        return false;
      }
    }
    return true;
  }

  function validarTodasFilasIndirectos() {
    const rows = getIndirectoRows();
    for (let i = 0; i < rows.length; i += 1) {
      if (filaIndirectoVacia(rows[i])) {
        continue;
      }
      if (!validarFilaIndirecto(rows[i], i + 1)) {
        return false;
      }
    }
    return validarIndirectosSinDuplicados();
  }

  function findDuplicateIndirecto(gastoId, excludeSelect) {
    if (!gastoId) return false;
    return Array.from(
      document.querySelectorAll('#tbody-indirectos select[name="indirecto_gasto"]')
    ).some((sel) => sel !== excludeSelect && sel.value === gastoId);
  }

  function validarIndirectosSinDuplicados() {
    const vistos = new Set();
    for (const sel of document.querySelectorAll(
      '#tbody-indirectos select[name="indirecto_gasto"]'
    )) {
      const gastoId = sel.value;
      if (!gastoId) continue;
      if (vistos.has(gastoId)) {
        avisar(mensajeIndirectoDuplicado(gastoId), "warning");
        sel.focus();
        return false;
      }
      vistos.add(gastoId);
    }
    return true;
  }

  function findDuplicateProducto(productoId, excludeSelect) {
    if (!productoId) return false;
    return Array.from(
      document.querySelectorAll('#tbody-ingredientes select[name="ingrediente_producto"]')
    ).some((sel) => sel !== excludeSelect && sel.value === productoId);
  }

  function validarIngredientesSinDuplicados() {
    const vistos = new Set();
    for (const sel of document.querySelectorAll(
      '#tbody-ingredientes select[name="ingrediente_producto"]'
    )) {
      const productoId = sel.value;
      if (!productoId) continue;
      if (vistos.has(productoId)) {
        avisarProductoDuplicado(mensajeProductoDuplicado(productoId));
        sel.focus();
        return false;
      }
      vistos.add(productoId);
    }
    return true;
  }

  function fillUnidadSelect(select, productoId, selected) {
    if (!select) return;
    const units =
      productoId && unidadesPorProducto[productoId]?.length
        ? unidadesPorProducto[productoId]
        : unidadesGlobal;
    const selectedNorm = (selected || "").trim();
    let html = '<option value="">Seleccionar…</option>';
    let found = false;
    units.forEach((u) => {
      const isSelected = u === selectedNorm;
      if (isSelected) found = true;
      html += `<option value="${u}"${isSelected ? " selected" : ""}>${u}</option>`;
    });
    if (selectedNorm && !found) {
      html += `<option value="${selectedNorm}" selected>${selectedNorm}</option>`;
    }
    select.innerHTML = html;
  }

  function cloneTemplate(id, tbodyId) {
    const tpl = document.getElementById(id);
    const tbody = document.getElementById(tbodyId);
    if (!tpl || !tbody) return;
    tbody.appendChild(tpl.content.cloneNode(true));
  }

  document.getElementById("btn-add-ingrediente")?.addEventListener("click", () => {
    if (!validarAntesDeAgregarIngrediente()) return;
    cloneTemplate("tpl-ingrediente-row", "tbody-ingredientes");
    const rows = getIngredienteRows();
    const nuevaFila = rows[rows.length - 1];
    nuevaFila?.querySelector('select[name="ingrediente_producto"]')?.focus();
  });
  document.getElementById("btn-add-indirecto")?.addEventListener("click", () => {
    if (!validarAntesDeAgregarIndirecto()) return;
    cloneTemplate("tpl-indirecto-row", "tbody-indirectos");
    const rows = getIndirectoRows();
    const nuevaFila = rows[rows.length - 1];
    nuevaFila?.querySelector('select[name="indirecto_gasto"]')?.focus();
  });
  document.getElementById("btn-add-paso")?.addEventListener("click", () => {
    cloneTemplate("tpl-paso-row", "tbody-pasos");
  });

  form.addEventListener("click", (event) => {
    const btn = event.target.closest(".btn-remove-row");
    if (!btn) return;
    const row = btn.closest("tr");
    if (row) row.remove();
  });

  document.getElementById("tbody-ingredientes")?.addEventListener("change", (event) => {
    const productoSelect = event.target.closest('select[name="ingrediente_producto"]');
    if (!productoSelect) return;

    const productoId = productoSelect.value;
    if (productoId && findDuplicateProducto(productoId, productoSelect)) {
      avisarProductoDuplicado(mensajeProductoDuplicado(productoId));
      productoSelect.value = "";
      const row = productoSelect.closest("tr");
      const unidadSelect = row?.querySelector(".ingrediente-unidad-select");
      fillUnidadSelect(unidadSelect, "", "");
      return;
    }

    const row = productoSelect.closest("tr");
    const unidadSelect = row?.querySelector(".ingrediente-unidad-select");
    fillUnidadSelect(unidadSelect, productoId, "");
  });

  document.getElementById("tbody-indirectos")?.addEventListener("change", (event) => {
    const gastoSelect = event.target.closest('select[name="indirecto_gasto"]');
    if (!gastoSelect) return;

    const gastoId = gastoSelect.value;
    if (gastoId && findDuplicateIndirecto(gastoId, gastoSelect)) {
      avisar(mensajeIndirectoDuplicado(gastoId), "warning");
      gastoSelect.value = "";
      gastoSelect.focus();
    }
  });

  form.addEventListener("submit", (event) => {
    if (!validarTodasFilasIngredientes() || !validarTodasFilasIndirectos()) {
      event.preventDefault();
    }
  });

  if (precioInput && overrideInput) {
    precioInput.addEventListener("input", () => {
      overrideInput.value = "1";
    });
  }
})();
