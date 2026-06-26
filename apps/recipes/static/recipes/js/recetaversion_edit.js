(() => {

  const form = document.getElementById("form-recetaversion-edit");

  if (!form) return;



  const CATALOGO_INDIRECTOS = {

    "Gas horno": { unidad_cobro: "hora", tarifa: 3.5 },

    "Luz cocina": { unidad_cobro: "mes", tarifa: 80 },

    "Mano de obra horneado": { unidad_cobro: "hora", tarifa: 5 },

    "Empaque porción": { unidad_cobro: "porcion", tarifa: 0.15 },

    "Flete semanal": { unidad_cobro: "lote", tarifa: 15 },

  };



  const DEMO = {

    1: {

      receta_id: 1,

      nombre: "Brownie clásico",

      version: 2,

      version_id: 12,

      rendimiento_cantidad: "12",

      rendimiento_unidad: "porciones",

      costo_ingredientes: "21.50",

      costo_indirectos: "3.00",

      costo_total: "24.50",

      costo_porcion: "2.04",

      precio_sugerido: "2.86",

      margen_aplicado_pct: "40.00",

      precio_override_manual: false,

      ingredientes: [

        { producto: "Harina de trigo", cantidad: "250", unidad: "g", costo: "1.13", aviso: null },

        { producto: "Chocolate semi amargo", cantidad: "200", unidad: "g", costo: "8.40", aviso: null },

        { producto: "Mantequilla", cantidad: "150", unidad: "g", costo: "6.75", aviso: null },

        { producto: "Huevo", cantidad: "3", unidad: "unidad", costo: "1.50", aviso: null },

        { producto: "Azúcar blanca", cantidad: "180", unidad: "g", costo: "0.72", aviso: null },

        { producto: "Vainilla", cantidad: "1", unidad: "cdta", costo: "—", aviso: "Sin conversión cdta→g; configure en Conversiones." },

      ],

      indirectos: [

        { gasto: "Gas horno", cantidad: "0.5", notas: "25 min horno", costo: "1.75" },

        { gasto: "Mano de obra horneado", cantidad: "0.25", notas: "Preparación + horneado", costo: "1.25" },

      ],

      pasos: [

        { orden: 1, instruccion: "Derretir chocolate con mantequilla a baño maría.", tiempo: "10" },

        { orden: 2, instruccion: "Batir huevos con azúcar hasta espumar ligeramente.", tiempo: "5" },

        { orden: 3, instruccion: "Incorporar harina tamizada sin batir en exceso.", tiempo: "3" },

        { orden: 4, instruccion: "Hornear 25 min a 180 °C. Enfriar antes de cortar.", tiempo: "25" },

      ],

    },

  };



  const params = new URLSearchParams(window.location.search);

  const recetaId = params.get("receta_id") || "1";

  const data = DEMO[recetaId];



  function setText(id, text) {

    const el = document.getElementById(id);

    if (el) el.textContent = text;

  }



  function calcCostoLineaIndirecto(gasto, cantidad) {

    const cat = CATALOGO_INDIRECTOS[gasto];

    if (!cat || cantidad === "" || Number.isNaN(parseFloat(cantidad))) return "—";

    const linea = parseFloat(cantidad) * cat.tarifa;

    return linea.toFixed(2);

  }



  function renderIngredientes(rows) {

    const tbody = document.getElementById("tbody-ingredientes");

    if (!tbody) return;

    tbody.innerHTML = "";

    rows.forEach((row, idx) => {

      const tr = document.createElement("tr");

      tr.dataset.rowIndex = String(idx);

      tr.innerHTML = `

        <td>

          <select name="ingrediente_producto_${idx}" aria-label="Producto fila ${idx + 1}">

            <option value="">— Seleccionar —</option>

            <option ${row.producto === "Harina de trigo" ? "selected" : ""}>Harina de trigo</option>

            <option ${row.producto === "Chocolate semi amargo" ? "selected" : ""}>Chocolate semi amargo</option>

            <option ${row.producto === "Mantequilla" ? "selected" : ""}>Mantequilla</option>

            <option ${row.producto === "Huevo" ? "selected" : ""}>Huevo</option>

            <option ${row.producto === "Azúcar blanca" ? "selected" : ""}>Azúcar blanca</option>

            <option ${row.producto === "Vainilla" ? "selected" : ""}>Vainilla</option>

          </select>

        </td>

        <td><input type="number" name="ingrediente_cantidad_${idx}" step="0.0001" min="0.0001" value="${row.cantidad}" aria-label="Cantidad"></td>

        <td><input type="text" name="ingrediente_unidad_${idx}" maxlength="20" value="${row.unidad}" aria-label="Unidad"></td>

        <td class="col-costo">${row.costo === "—" ? "—" : `$ ${row.costo}`}</td>

        <td class="table-actions"><button type="button" class="btn-remove-ing" data-index="${idx}">Quitar</button></td>

      `;

      tbody.appendChild(tr);

      if (row.aviso) {

        const aviso = document.createElement("tr");

        aviso.className = "row-aviso";

        aviso.innerHTML = `<td colspan="5">⚠ ${row.aviso}</td>`;

        tbody.appendChild(aviso);

      }

    });

  }



  function renderIndirectos(rows) {

    const tbody = document.getElementById("tbody-indirectos");

    if (!tbody) return;

    tbody.innerHTML = "";

    const opciones = Object.keys(CATALOGO_INDIRECTOS);

    rows.forEach((row, idx) => {

      const cat = CATALOGO_INDIRECTOS[row.gasto] || { unidad_cobro: "—", tarifa: 0 };

      const tr = document.createElement("tr");

      tr.dataset.rowIndex = String(idx);

      tr.innerHTML = `

        <td>

          <select name="indirecto_gasto_${idx}" class="indirecto-gasto-select" data-index="${idx}" aria-label="Gasto indirecto fila ${idx + 1}">

            <option value="">— Seleccionar —</option>

            ${opciones.map((n) => `<option value="${n}" ${row.gasto === n ? "selected" : ""}>${n}</option>`).join("")}

          </select>

        </td>

        <td><input type="number" name="indirecto_cantidad_${idx}" class="indirecto-cantidad-input" data-index="${idx}" step="0.0001" min="0" value="${row.cantidad}" aria-label="Cantidad"></td>

        <td class="col-unidad" data-unidad-cell="${idx}">${cat.unidad_cobro}</td>

        <td class="col-costo" data-costo-cell="${idx}">${row.costo === "—" ? "—" : `$ ${row.costo}`}</td>

        <td class="col-notas"><input type="text" name="indirecto_notas_${idx}" maxlength="100" value="${row.notas || ""}" placeholder="Opcional" aria-label="Notas"></td>

        <td class="table-actions"><button type="button" class="btn-remove-ind" data-index="${idx}">Quitar</button></td>

      `;

      tbody.appendChild(tr);

    });

  }



  function refreshIndirectoRow(idx) {

    const gasto = indirectos[idx]?.gasto;

    const cantidad = indirectos[idx]?.cantidad ?? "";

    const cat = CATALOGO_INDIRECTOS[gasto];

    const unidadCell = document.querySelector(`[data-unidad-cell="${idx}"]`);

    const costoCell = document.querySelector(`[data-costo-cell="${idx}"]`);

    if (unidadCell) unidadCell.textContent = cat ? cat.unidad_cobro : "—";

    const costo = calcCostoLineaIndirecto(gasto, cantidad);

    if (costoCell) costoCell.textContent = costo === "—" ? "—" : `$ ${costo}`;

    if (indirectos[idx]) indirectos[idx].costo = costo;

  }



  function renderPasos(pasos) {

    const list = document.getElementById("lista-pasos");

    if (!list) return;

    list.innerHTML = "";

    pasos.forEach((paso, idx) => {

      const li = document.createElement("li");

      li.className = "recetaversion-paso-item";

      li.dataset.pasoIndex = String(idx);

      li.innerHTML = `

        <span class="recetaversion-paso-orden" aria-hidden="true">${paso.orden}</span>

        <div class="recetaversion-paso-fields">

          <textarea name="paso_instruccion_${idx}" rows="2" required aria-required="true" placeholder="Instrucción del paso…">${paso.instruccion}</textarea>

          <label class="form-hint" style="margin:0;">

            Tiempo (min, opcional)

            <input type="number" class="recetaversion-paso-tiempo" name="paso_tiempo_${idx}" min="1" step="1" value="${paso.tiempo || ""}" placeholder="—">

          </label>

        </div>

        <div class="recetaversion-paso-actions">

          <button type="button" class="btn-paso-up" data-index="${idx}" title="Subir">↑</button>

          <button type="button" class="btn-paso-down" data-index="${idx}" title="Bajar">↓</button>

          <button type="button" class="btn-remove-paso btn-remove" data-index="${idx}">Quitar</button>

        </div>

      `;

      list.appendChild(li);

    });

  }



  if (!data) {

    BakeBudgeModal.showError(`Receta #${recetaId} sin versión vigente (demo).`);

    return;

  }



  form.receta_id.value = String(data.receta_id);

  form.version_id.value = String(data.version_id);

  setText("ctx-nombre", data.nombre);

  setText("ctx-version", `v${data.version} · vigente`);

  setText("stat-ingredientes", `$ ${data.costo_ingredientes}`);

  setText("stat-indirectos", `$ ${data.costo_indirectos}`);

  setText("stat-total", `$ ${data.costo_total}`);

  setText("stat-porcion", `$ ${data.costo_porcion}`);

  const margenPct = parseFloat(data.margen_aplicado_pct) || 40;
  const precioCalculado = calcPrecioDesdeMargen(parseFloat(data.costo_porcion), margenPct);

  form.precio_venta_sugerido.value = data.precio_sugerido;
  form.margen_aplicado_pct.value = data.margen_aplicado_pct;
  const margenDisplay = document.getElementById("margen_aplicado_display");
  if (margenDisplay) margenDisplay.value = `${data.margen_aplicado_pct} %`;
  setText("precio-calculado-valor", `$ ${precioCalculado.toFixed(2)}`);

  let precioOverride = Boolean(data.precio_override_manual);
  actualizarBadgeOverride(precioOverride);

  function calcPrecioDesdeMargen(costoPorcion, margen) {
    if (Number.isNaN(costoPorcion) || costoPorcion <= 0) return 0;
    return costoPorcion * (1 + margen / 100);
  }

  function actualizarBadgeOverride(activo) {
    const badge = document.getElementById("precio-override-badge");
    const hidden = document.getElementById("precio_override_manual");
    if (badge) badge.hidden = !activo;
    if (hidden) hidden.value = activo ? "1" : "0";
    precioOverride = activo;
  }

  form.precio_venta_sugerido?.addEventListener("input", () => {
    const calc = precioCalculado.toFixed(2);
    const actual = parseFloat(form.precio_venta_sugerido.value);
    const esManual = !Number.isNaN(actual) && actual.toFixed(2) !== calc;
    actualizarBadgeOverride(esManual);
  });

  document.getElementById("btn-recalcular-precio")?.addEventListener("click", () => {
    form.precio_venta_sugerido.value = precioCalculado.toFixed(2);
    actualizarBadgeOverride(false);
    BakeBudgeModal.showSuccess(`Precio sugerido actualizado al cálculo automático: $ ${precioCalculado.toFixed(2)} (demo).`);
  });



  form.rendimiento_cantidad.value = data.rendimiento_cantidad;

  form.rendimiento_unidad.value = data.rendimiento_unidad;



  let ingredientes = [...data.ingredientes];

  let indirectos = [...data.indirectos];

  let pasos = [...data.pasos];



  renderIngredientes(ingredientes);

  renderIndirectos(indirectos);

  renderPasos(pasos);



  document.getElementById("btn-add-ingrediente")?.addEventListener("click", () => {

    ingredientes.push({ producto: "", cantidad: "1", unidad: "g", costo: "0.00", aviso: null });

    renderIngredientes(ingredientes);

  });



  document.getElementById("tbody-ingredientes")?.addEventListener("click", (e) => {

    const btn = e.target.closest(".btn-remove-ing");

    if (!btn) return;

    const idx = parseInt(btn.dataset.index, 10);

    ingredientes.splice(idx, 1);

    renderIngredientes(ingredientes);

  });



  document.getElementById("btn-add-indirecto")?.addEventListener("click", () => {

    indirectos.push({ gasto: "", cantidad: "1", notas: "", costo: "0.00" });

    renderIndirectos(indirectos);

  });



  document.getElementById("tbody-indirectos")?.addEventListener("click", (e) => {

    const btn = e.target.closest(".btn-remove-ind");

    if (!btn) return;

    const idx = parseInt(btn.dataset.index, 10);

    indirectos.splice(idx, 1);

    renderIndirectos(indirectos);

  });



  document.getElementById("tbody-indirectos")?.addEventListener("change", (e) => {

    const sel = e.target.closest(".indirecto-gasto-select");

    if (!sel) return;

    const idx = parseInt(sel.dataset.index, 10);

    indirectos[idx].gasto = sel.value;

    refreshIndirectoRow(idx);

  });



  document.getElementById("tbody-indirectos")?.addEventListener("input", (e) => {

    const inp = e.target.closest(".indirecto-cantidad-input");

    if (!inp) return;

    const idx = parseInt(inp.dataset.index, 10);

    indirectos[idx].cantidad = inp.value;

    refreshIndirectoRow(idx);

  });



  document.getElementById("btn-add-paso")?.addEventListener("click", () => {

    const next = pasos.length ? Math.max(...pasos.map((p) => p.orden)) + 1 : 1;

    pasos.push({ orden: next, instruccion: "", tiempo: "" });

    renderPasos(pasos);

  });



  document.getElementById("lista-pasos")?.addEventListener("click", (e) => {

    const up = e.target.closest(".btn-paso-up");

    const down = e.target.closest(".btn-paso-down");

    const rem = e.target.closest(".btn-remove-paso");

    if (up) {

      const idx = parseInt(up.dataset.index, 10);

      if (idx > 0) {

        [pasos[idx - 1], pasos[idx]] = [pasos[idx], pasos[idx - 1]];

        pasos.forEach((p, i) => { p.orden = i + 1; });

        renderPasos(pasos);

      }

      return;

    }

    if (down) {

      const idx = parseInt(down.dataset.index, 10);

      if (idx < pasos.length - 1) {

        [pasos[idx], pasos[idx + 1]] = [pasos[idx + 1], pasos[idx]];

        pasos.forEach((p, i) => { p.orden = i + 1; });

        renderPasos(pasos);

      }

      return;

    }

    if (rem) {

      const idx = parseInt(rem.dataset.index, 10);

      pasos.splice(idx, 1);

      pasos.forEach((p, i) => { p.orden = i + 1; });

      renderPasos(pasos);

    }

  });



  form.addEventListener("submit", (event) => {

    event.preventDefault();

    const rend = parseFloat(form.rendimiento_cantidad.value);

    const rendUnidad = form.rendimiento_unidad.value.trim();

    if (form.rendimiento_cantidad.value.trim() === "" || Number.isNaN(rend) || rend <= 0) {

      BakeBudgeModal.showError("El rendimiento debe ser mayor que 0.");

      form.rendimiento_cantidad.focus();

      return;

    }

    if (!rendUnidad) {

      BakeBudgeModal.showError("Indica la unidad de rendimiento.");

      form.rendimiento_unidad.focus();

      return;

    }

    if (ingredientes.length === 0) {

      BakeBudgeModal.showError("Agrega al menos un ingrediente.");

      return;

    }

    for (let i = 0; i < ingredientes.length; i++) {

      const sel = form.querySelector(`[name="ingrediente_producto_${i}"]`);

      const cant = form.querySelector(`[name="ingrediente_cantidad_${i}"]`);

      if (!sel?.value) {

        BakeBudgeModal.showError(`Selecciona el producto en la fila ${i + 1}.`);

        sel?.focus();

        return;

      }

      const c = parseFloat(cant?.value);

      if (!cant?.value.trim() || Number.isNaN(c) || c <= 0) {

        BakeBudgeModal.showError(`La cantidad debe ser mayor que 0 (fila ${i + 1}).`);

        cant?.focus();

        return;

      }

    }

    const gastosUsados = new Set();

    for (let i = 0; i < indirectos.length; i++) {

      const sel = form.querySelector(`[name="indirecto_gasto_${i}"]`);

      const cant = form.querySelector(`[name="indirecto_cantidad_${i}"]`);

      if (!sel?.value) {

        BakeBudgeModal.showError(`Selecciona el gasto indirecto en la fila ${i + 1}.`);

        sel?.focus();

        return;

      }

      if (gastosUsados.has(sel.value)) {

        BakeBudgeModal.showError(`«${sel.value}» ya está asignado en esta versión.`);

        sel.focus();

        return;

      }

      gastosUsados.add(sel.value);

      const c = parseFloat(cant?.value);

      if (cant?.value.trim() === "" || Number.isNaN(c) || c < 0) {

        BakeBudgeModal.showError(`La cantidad del indirecto debe ser ≥ 0 (fila ${i + 1}).`);

        cant?.focus();

        return;

      }

    }

    for (let i = 0; i < pasos.length; i++) {

      const ta = form.querySelector(`[name="paso_instruccion_${i}"]`);

      if (!ta?.value.trim()) {

        BakeBudgeModal.showError(`La instrucción del paso ${i + 1} es obligatoria.`);

        ta?.focus();

        return;

      }

    }

    const precio = parseFloat(form.precio_venta_sugerido.value);
    if (form.precio_venta_sugerido.value.trim() === "" || Number.isNaN(precio) || precio <= 0) {
      BakeBudgeModal.showError("El precio sugerido debe ser mayor que 0.");
      form.precio_venta_sugerido.focus();
      return;
    }

    const nInd = indirectos.length;
    const overrideNote = precioOverride ? " (precio manual)" : "";
    BakeBudgeModal.showSuccess(
      `Formulación v${data.version} de «${data.nombre}» guardada — ` +
        `${ingredientes.length} ingredientes, ${nInd} indirecto(s), precio $ ${precio.toFixed(2)}${overrideNote} (demo).`
    );

  });

})();

